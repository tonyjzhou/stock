#!/usr/bin/env python
import argparse
import logging
import math
import statistics
from datetime import datetime

from tabulate import tabulate
from yahooquery import Ticker

from database import DatabaseManager

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_financial_data(ticker, data_type, frequency='Annual'):
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


def strip_nan(ns):
    return [n for n in ns if not math.isnan(n)]


def process_financial_data(data, data_key):
    try:
        processed_data = data[['asOfDate', data_key]].set_index('asOfDate')
        return strip_nan(processed_data.to_dict()[data_key].values())
    except Exception as e:
        logging.error(f"Error in processing data: {e}")
        return []


def average_financial_metric(ticker, data_type, data_key):
    data = fetch_financial_data(ticker, data_type)
    if data is None:
        return 0
    try:
        return statistics.fmean(process_financial_data(data, data_key))
    except Exception as e:
        logging.error(f"Error calculating average for {data_key}: {e}")
        return 0


# Redefine functions like average_free_cash_flow and average_common_stock_equity
# to use average_financial_metric with appropriate parameters.

def has_consecutive_positive_fcf(ticker):
    cash_flow = fetch_financial_data(ticker, 'cash_flow')
    if cash_flow is None:
        return False
    free_cash_flows = process_financial_data(cash_flow, 'FreeCashFlow')
    return all(v > 0 for v in free_cash_flows)


def has_good_return_on_equity(ticker, verbose=False):
    average_fcf = average_financial_metric(ticker, 'cash_flow', 'FreeCashFlow')
    average_cse = average_financial_metric(ticker, 'balance_sheet', 'CommonStockEquity')
    if average_fcf <= 0 or average_cse <= 0:
        if verbose:
            logging.info(f"{ticker.symbols} does not meet ROE criteria: FCF={average_fcf}, CSE={average_cse}")
        return False, 0

    average_roe = average_fcf / average_cse
    if verbose:
        logging.info(f"{ticker.symbols} average_roe={average_roe}")
    return average_roe > 0.13, average_roe


def _has_consistently_low_ratios(ratios, threshold=0.4):
    return all([ratio < threshold or math.isnan(ratio) for ratio in ratios])


def has_consistently_low_debt_ratios(ticker, verbose):
    balance_sheet = ticker.balance_sheet(frequency='Quarterly')

    if isinstance(balance_sheet, str):
        if verbose:
            logging.info(f"Error: balance sheet for {ticker.symbols} is a string: {balance_sheet}")
        return False

    if balance_sheet is None or balance_sheet.empty or 'CommonStockEquity' not in balance_sheet.columns:
        if verbose:
            logging.info(f"No CommonStockEquity data available for {ticker.symbols}")
        return False

    try:
        balance_sheet['TotalDebt/CommonStockEquity'] = balance_sheet['TotalDebt'] / balance_sheet['CommonStockEquity']
    except KeyError:
        if verbose:
            logging.info(f"Required data missing in balance sheet for {ticker.symbols}")
        return False

    debt_equity_ratio = balance_sheet[['asOfDate', 'TotalDebt/CommonStockEquity']]
    debt_equity_ratio = debt_equity_ratio.set_index('asOfDate').to_dict()['TotalDebt/CommonStockEquity']
    debt_equity_ratio_values = list(debt_equity_ratio.values())

    if not _has_consistently_low_ratios(debt_equity_ratio_values):
        if verbose:
            logging.info(f"{ticker.symbols} doesn't have consistently low debt ratios: {debt_equity_ratio_values}")
        return False

    return True


def has_consistently_low_goodwill_ratios(ticker, verbose):
    balance_sheet = ticker.balance_sheet(frequency='Quarterly')

    if isinstance(balance_sheet, str):
        if verbose:
            logging.info(f"Error: balance sheet for {ticker.symbols} is a string: {balance_sheet}")
        return False

    if balance_sheet is None or balance_sheet.empty or 'CommonStockEquity' not in balance_sheet.columns:
        if verbose:
            logging.info(f"No CommonStockEquity data available for {ticker.symbols}")
        return False

    try:
        balance_sheet['GoodwillAndOtherIntangibleAssets/CommonStockEquity'] = balance_sheet[
                                                                                  'GoodwillAndOtherIntangibleAssets'] / \
                                                                              balance_sheet['CommonStockEquity']
    except KeyError:
        if verbose:
            logging.info(f"Required data missing in balance sheet for {ticker.symbols}")
        return False

    goodwill_equity_ratio = balance_sheet[['asOfDate', 'GoodwillAndOtherIntangibleAssets/CommonStockEquity']]
    goodwill_equity_ratio = goodwill_equity_ratio.set_index('asOfDate').to_dict()[
        'GoodwillAndOtherIntangibleAssets/CommonStockEquity']
    goodwill_equity_ratio_values = list(goodwill_equity_ratio.values())

    if not _has_consistently_low_ratios(goodwill_equity_ratio_values):
        if verbose:
            logging.info(f"{ticker.symbols} doesn't have consistently low goodwill ratios: {goodwill_equity_ratio_values}")
        return False

    return True


def has_processed(symbol):
    with DatabaseManager() as db:
        rows = db.read_data(symbol)
        if not rows:
            return False

        symbol, tested_at = rows[0]
        tested_at = datetime.strptime(tested_at, '%Y-%m-%d %H:%M:%S.%f')
        return (datetime.now() - tested_at).days < 365


def is_volatile(ticker, symbol, threshold=0.5, verbose=False):
    if symbol not in ticker.summary_detail:
        if verbose:
            logging.info(f"Error: No summary detail found for {symbol}")
        return False, 0, 0, 0

    summary_detail = ticker.summary_detail[symbol]

    if summary_detail is None:
        if verbose:
            logging.info(f"Error: No summary detail found for {symbol}")
        return False, 0, 0, 0

    if not isinstance(summary_detail, dict):
        if verbose:
            logging.info(f"Error: summary detail for {symbol} is not a dictionary: {summary_detail}")
        return False, 0, 0, 0

    if 'fiftyTwoWeekLow' not in summary_detail or 'fiftyTwoWeekHigh' not in summary_detail:
        if verbose:
            logging.info(f"Error: Required data missing in summary detail for {symbol}")
        return False, 0, 0, 0

    fifty_two_week_low = summary_detail['fiftyTwoWeekLow']
    fifty_two_week_high = summary_detail['fiftyTwoWeekHigh']
    fifty_two_week_diff = fifty_two_week_high - fifty_two_week_low

    volatility = fifty_two_week_diff / fifty_two_week_low

    return volatility >= threshold, volatility, fifty_two_week_low, fifty_two_week_high


def test_strong_buy(symbol, verbose):
    if has_processed(symbol):
        logging.info(f"{symbol} has already been processed")
        return None  # Return None if already processed
    else:
        with DatabaseManager() as db:
            db.insert_data(symbol, datetime.now())

            ticker = Ticker(symbol)
            if verbose:
                logging.info(f"{ticker.symbols}'s exchange is: {ticker.price[symbol]['exchangeName']}")

            volatile, volatility, fifty_two_week_low, fifty_two_week_high = is_volatile(ticker, symbol, verbose=verbose)

            if not volatile:
                if verbose:
                    logging.info(f"{ticker.symbols}  is not volatile enough: {round(volatility * 100, 2)}%")
                return None  # Return None if not volatile

            good_roe, roe = has_good_return_on_equity(ticker, verbose=verbose)

            if not good_roe:
                if verbose:
                    logging.info(f"{ticker.symbols} doesn't have good return on equity: {round(roe * 100, 2)}%")
                return None  # Return None if ROE not good

            if not has_consistently_low_debt_ratios(ticker, verbose=verbose):
                if verbose:
                    logging.info(f"{ticker.symbols} doesn't have consistently low debt ratios")
                return None  # Return None if balance sheet not strong

            if not has_consistently_low_goodwill_ratios(ticker, verbose=verbose):
                if verbose:
                    logging.info(f"{ticker.symbols} doesn't have consistently low goodwill ratios")
                return None  # Return None if balance sheet not strong

            logging.info(
                f"{ticker.symbols} has a strong business with ROE: {round(roe * 100, 2)}%\n")

            return {
                'Symbol': ticker.symbols,
                'ROE': round(roe * 100, 2),
                'Volatility': volatility,
                '52-week low': fifty_two_week_low,
                '52-week high': fifty_two_week_high,
                'Market': ticker.price[symbol]['exchangeName'],
            }


def main():
    parser = argparse.ArgumentParser(description='Test if a stock has a strong business.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()

    strong_businesses = []
    with open("tickers.txt", "r") as file:
        for line in file:
            symbol = line.strip()
            is_strong = test_strong_buy(symbol, args.verbose)
            if is_strong:
                strong_businesses.append(is_strong)
            logging.info(f"Processed ticker: {symbol}")

    if strong_businesses:
        strong_businesses.sort(key=lambda x: x['ROE'], reverse=True)
        logging.info(f'\n{tabulate(strong_businesses, headers="keys")}')


if __name__ == '__main__':
    main()
