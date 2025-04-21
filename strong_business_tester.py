#!/usr/bin/env python
import argparse
import asyncio
import logging
import math
import os
import statistics
from datetime import datetime
from logging.handlers import RotatingFileHandler
import csv  # <-- Added import for CSV handling

from yahooquery import Ticker

from database import DatabaseManager


def format_table_markdown(data):
    """Format a list of dictionaries as a markdown table."""
    if not data:
        return ""

    # Get headers from the first dictionary
    headers = list(data[0].keys())

    # Create header row
    header_row = "| " + " | ".join(headers) + " |"

    # Create separator row
    separator_row = "| " + " | ".join(["---" for _ in headers]) + " |"

    # Create data rows
    data_rows = []
    for row in data:
        data_rows.append(
            "| " + " | ".join(str(row[header]) for header in headers) + " |"
        )

    # Combine all rows
    return "\n".join([header_row, separator_row] + data_rows)


# Set up logging to both console and a file
logger = logging.getLogger()  # Get the root logger
logger.setLevel(logging.INFO)

# Create a formatter to define the log output format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Get the current program name and set the log file name
program_name = os.path.splitext(os.path.basename(__file__))[0]
log_file_name = f"{program_name}.log"

# Create a file handler with the program's log file name
file_handler = RotatingFileHandler(log_file_name, maxBytes=0, backupCount=3)
file_handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(file_handler)


def fetch_financial_data(ticker, data_type, frequency="Annual"):
    """
    Fetch financial data for a given ticker.
    """
    try:
        data = getattr(ticker, data_type)(frequency=frequency)
        if data is None or isinstance(data, str) or data.empty:
            logging.warning(f"No {data_type} data available for {ticker.symbols}")
            return None
        return data
    except Exception as e:
        logging.error(f"Error fetching {data_type} data for {ticker.symbols}: {e}")
        return None


def strip_nan(values):
    """Remove NaN values from a list."""
    return [value for value in values if not math.isnan(value)]


def process_financial_data(data, data_key):
    """
    Process financial data to extract a list of values for a given key.
    """
    try:
        processed_data = data[["asOfDate", data_key]].set_index("asOfDate")
        return strip_nan(processed_data[data_key].values)
    except Exception as e:
        logging.error(f"Error in processing data: {e}")
        return []


def average_financial_metric(ticker, data_type, data_key):
    """
    Calculate the average of a financial metric for a ticker.
    """
    data = fetch_financial_data(ticker, data_type)
    if data is None:
        return 0
    try:
        values = process_financial_data(data, data_key)
        return statistics.fmean(values) if values else 0
    except Exception as e:
        logging.error(f"Error calculating average for {data_key}: {e}")
        return 0


def has_good_return_on_equity(ticker, roe_threshold, verbose=False):
    """
    Determine if the ticker has a good return on equity.
    """
    average_fcf = average_financial_metric(ticker, "cash_flow", "FreeCashFlow")
    average_cse = average_financial_metric(ticker, "balance_sheet", "CommonStockEquity")
    if average_fcf <= 0 or average_cse <= 0:
        if verbose:
            logging.info(
                f"{ticker.symbols} does not meet ROE criteria: "
                f"FCF={average_fcf}, CSE={average_cse}"
            )
        return False, 0

    average_roe = average_fcf / average_cse
    if verbose:
        logging.info(f"{ticker.symbols} average ROE={average_roe}")
    return average_roe > roe_threshold, average_roe


def _has_consistently_low_ratios(ratios, threshold=0.4):
    """Check if all ratios are below the threshold."""
    return all(ratio < threshold or math.isnan(ratio) for ratio in ratios)


def has_consistently_low_debt_ratios(ticker, verbose):
    """
    Check if the ticker has consistently low debt-to-equity ratios.
    """
    balance_sheet = fetch_financial_data(ticker, "balance_sheet", frequency="Quarterly")
    if balance_sheet is None or "CommonStockEquity" not in balance_sheet.columns:
        if verbose:
            logging.info(f"No CommonStockEquity data available for {ticker.symbols}")
        return False

    try:
        balance_sheet["DebtEquityRatio"] = (
            balance_sheet["TotalDebt"] / balance_sheet["CommonStockEquity"]
        )
    except KeyError as e:
        if verbose:
            logging.info(
                f"Required data missing in balance sheet for {ticker.symbols}: {e}"
            )
        return False

    debt_equity_ratios = process_financial_data(balance_sheet, "DebtEquityRatio")
    if not _has_consistently_low_ratios(debt_equity_ratios):
        if verbose:
            logging.info(
                f"{ticker.symbols} doesn't have consistently low debt ratios: "
                f"{debt_equity_ratios}"
            )
        return False

    return True


async def has_processed(symbol, lock, process_interval):
    async with DatabaseManager(lock=lock) as db:
        rows = await db.read_data(symbol)
        if not rows:
            return False

        symbol, tested_at = rows[0]
        tested_at = datetime.strptime(tested_at, "%Y-%m-%d %H:%M:%S.%f")
        return (datetime.now() - tested_at).days < process_interval


async def is_volatile(ticker, symbol, threshold=0.5, verbose=False):
    """
    Determine if the stock is volatile based on its 52-week high and low.
    """
    try:
        summary_detail = ticker.summary_detail
        if symbol not in summary_detail:
            if verbose:
                logging.info(f"Error: No summary detail found for {symbol}")
            return False, 0, 0, 0

        detail = summary_detail[symbol]
        if isinstance(detail, dict):
            fifty_two_week_low = detail.get("fiftyTwoWeekLow")
            fifty_two_week_high = detail.get("fiftyTwoWeekHigh")
        else:
            if verbose:
                logging.warning(
                    f"Unexpected summary detail format for {symbol}: {detail}"
                )
            return False, 0, 0, 0

        if not fifty_two_week_low or not fifty_two_week_high:
            if verbose:
                logging.info(f"Error: Missing 52-week data for {symbol}")
            return False, 0, 0, 0

        fifty_two_week_diff = fifty_two_week_high - fifty_two_week_low
        volatility = fifty_two_week_diff / fifty_two_week_low
        return (
            volatility >= threshold,
            volatility,
            fifty_two_week_low,
            fifty_two_week_high,
        )

    except Exception as e:
        if verbose:
            logging.error(f"Error fetching volatility data for {symbol}: {e}")
        return False, 0, 0, 0


async def test_strong_buy(
    symbol, roe_threshold, volatility_threshold, verbose, lock, process_interval
):
    """
    Test if a stock is a strong buy based on various financial criteria.
    """
    if await has_processed(symbol, lock, process_interval):
        logging.info(f"{symbol} has already been processed")
        return None
    else:
        async with DatabaseManager(lock=lock) as db:
            await db.insert_data(symbol, datetime.now())

    ticker = Ticker(symbol, asynchronous=True)
    if verbose:
        price_data = ticker.price
        if price_data and symbol in price_data:
            if isinstance(price_data[symbol], dict):
                exchange_name = price_data[symbol].get("exchangeName", "Unknown")
                logging.info(f"{symbol}'s exchange is: {exchange_name}")
            else:
                logging.warning(
                    f"Unexpected data format for {symbol}: {price_data[symbol]}"
                )
        else:
            logging.warning(f"No price data found for {symbol}")

    volatile, volatility, fifty_two_week_low, fifty_two_week_high = await is_volatile(
        ticker, symbol, threshold=volatility_threshold, verbose=verbose
    )

    if not volatile:
        if verbose:
            logging.info(
                f"{symbol} is not volatile enough: {round(volatility * 100, 2)}%"
            )
        return None

    good_roe, roe = has_good_return_on_equity(ticker, roe_threshold, verbose=verbose)

    if not good_roe:
        if verbose:
            logging.info(
                f"{symbol} doesn't have good return on equity: {round(roe * 100, 2)}%"
            )
        return None

    if not has_consistently_low_debt_ratios(ticker, verbose=verbose):
        if verbose:
            logging.info(f"{symbol} doesn't have consistently low debt ratios")
        return None

    logging.info(f"{symbol} has a strong business with ROE: {round(roe * 100, 2)}%")
    price_data = ticker.price
    if price_data and symbol in price_data and isinstance(price_data[symbol], dict):
        market = price_data[symbol].get("exchangeName", "Unknown")
    else:
        market = "Unknown"
    return {
        "Symbol": symbol,
        "ROE": round(roe * 100, 2),
        "Volatility": round(volatility * 100, 2),
        "52-week Low": fifty_two_week_low,
        "52-week High": fifty_two_week_high,
        "Market": market,
    }


async def main():
    parser = argparse.ArgumentParser(
        description="Test if a stock has a strong business."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument(
        "--roe-threshold", type=float, default=0.17, help="Minimum ROE threshold"
    )
    parser.add_argument(
        "--volatility-threshold",
        type=float,
        default=0.7,
        help="Minimum volatility threshold",
    )
    parser.add_argument(
        "-c",
        "--csv-file",
        type=str,
        default="Results.csv",
        help="Path to the input CSV file",
    )  # Added argument for CSV file
    parser.add_argument(
        "--process-interval",
        type=int,
        default=180,
        help="Number of days before reprocessing a symbol (default: 180)",
    )
    args = parser.parse_args()

    lock = asyncio.Lock()
    tasks = []

    # Use the passed CSV file path
    with open(args.csv_file, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row["Symbol"].strip()
            tasks.append(
                test_strong_buy(
                    symbol,
                    args.roe_threshold,
                    args.volatility_threshold,
                    args.verbose,
                    lock,
                    args.process_interval,
                )
            )
            logging.info(f"Processing ticker: {symbol}")

    results = await asyncio.gather(*tasks)
    strong_businesses = [result for result in results if result is not None]

    if strong_businesses:
        strong_businesses.sort(key=lambda x: x["ROE"], reverse=True)
        markdown_table = format_table_markdown(strong_businesses)
        logging.info(f"\n{markdown_table}")


if __name__ == "__main__":
    asyncio.run(main())
