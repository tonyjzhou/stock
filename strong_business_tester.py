#!/usr/bin/env python
import argparse
import math
import statistics
from datetime import datetime

from yahooquery import Ticker

from database import insert_data, read_data


def has_consecutive_positive_fcf(ticker):
    """
    This filter will rule out Amazon and MU as strong business because they have negative FCF in some years.

    :param ticker:
    :return:
    """
    cash_flow = ticker.cash_flow(frequency='Annual')

    if cash_flow is None or isinstance(cash_flow, str) or cash_flow.empty or 'FreeCashFlow' not in cash_flow.columns:
        print(f"No FreeCashFlow data available for {ticker.symbols}")
        return False

    return all([v > 0 for v in (all_free_cash_flows(cash_flow))])


def all_free_cash_flows(cash_flow):
    free_cash_flows = cash_flow[['asOfDate', 'FreeCashFlow']].set_index('asOfDate')
    return strip_nan(free_cash_flows.to_dict()['FreeCashFlow'].values())


def all_common_stock_equities(balance_sheet):
    common_stock_equities = balance_sheet[['asOfDate', 'CommonStockEquity']].set_index('asOfDate')
    return strip_nan(common_stock_equities.to_dict()['CommonStockEquity'].values())


def strip_nan(ns):
    return [n for n in ns if not math.isnan(n)]


def average_free_cash_flow(ticker, verbose=False):
    cash_flow = ticker.cash_flow(frequency='Annual')

    if cash_flow is None or isinstance(cash_flow, str) or cash_flow.empty or 'FreeCashFlow' not in cash_flow.columns:
        if verbose:
            print(f"No FreeCashFlow data available for {ticker.symbols}")
        return 0

    return statistics.fmean(all_free_cash_flows(cash_flow))


def average_common_stock_equity(ticker, verbose=False):
    balance_sheet = ticker.balance_sheet(frequency='Annual')

    if balance_sheet is None or isinstance(balance_sheet,
                                           str) or balance_sheet.empty or 'CommonStockEquity' not in balance_sheet.columns:
        if verbose:
            print(f"No CommonStockEquity data available for {ticker.symbols}")
        return 0

    return statistics.fmean(all_common_stock_equities(balance_sheet))


def has_good_return_on_equity(ticker, verbose=False):
    average_fcf = average_free_cash_flow(ticker, verbose=verbose)
    if average_fcf <= 0:
        if verbose:
            print(f"{ticker.symbols} has non-positive average_fcf: {average_fcf}")
        return False

    average_cse = average_common_stock_equity(ticker)
    if average_cse <= 0:
        if verbose:
            print(f"{ticker.symbols} has non-positive average_cse: {average_cse}")
        return False

    average_roe = average_fcf / average_cse

    if verbose:
        print(f"{ticker.symbols} average_roe={average_roe}")

    return average_roe > 0.13


def has_consistently_low_debt_ratios(debt_equity_ratio_values, threshold=3):
    return all([v < threshold for v in debt_equity_ratio_values])


def has_strong_balance_sheet(ticker, verbose):
    balance_sheet = ticker.balance_sheet(frequency='Quarterly')

    if isinstance(balance_sheet, str):
        if verbose:
            print(f"Error: balance sheet for {ticker.symbols} is a string: {balance_sheet}")
        return False

    if balance_sheet is None or balance_sheet.empty or 'CommonStockEquity' not in balance_sheet.columns:
        if verbose:
            print(f"No CommonStockEquity data available for {ticker.symbols}")
        return False

    try:
        balance_sheet['TotalDebt/CommonStockEquity'] = balance_sheet['TotalDebt'] / balance_sheet['CommonStockEquity']
    except KeyError:
        if verbose:
            print(f"Required data missing in balance sheet for {ticker.symbols}")
        return False

    debt_equity_ratio = balance_sheet[['asOfDate', 'TotalDebt/CommonStockEquity']]
    debt_equity_ratio = debt_equity_ratio.set_index('asOfDate').to_dict()['TotalDebt/CommonStockEquity']
    debt_equity_ratio_values = list(debt_equity_ratio.values())

    if not has_consistently_low_debt_ratios(debt_equity_ratio_values):
        if verbose:
            print(f"{ticker.symbols} doesn't have consistently low debt ratios: {debt_equity_ratio_values}")
        return False

    return True


def has_processed(symbol):
    rows = read_data(symbol)
    if not rows:
        return False

    symbol, tested_at = rows[0]
    tested_at = datetime.strptime(tested_at, '%Y-%m-%d %H:%M:%S.%f')
    return (datetime.now() - tested_at).days < 365


def test_strong_business(symbol, verbose):
    if has_processed(symbol):
        print(f"{symbol} has already been processed\n")
        return False
    else:
        insert_data(symbol, datetime.now())

        ticker = Ticker(symbol)
        # if not has_consecutive_positive_fcf(ticker):
        #     if verbose:
        #         print(f"{ticker.symbols} doesn't have consecutive positive fcf")
        #     return False

        if not has_good_return_on_equity(ticker, verbose=verbose):
            if verbose:
                print(f"{ticker.symbols} doesn't have good return on equity")
            return False

        if not has_strong_balance_sheet(ticker, verbose=verbose):
            if verbose:
                print(f"{ticker.symbols} doesn't have strong balance sheet")
            return False

        print(f"{ticker.symbols} has a strong business\n")
        return True


def main():
    parser = argparse.ArgumentParser(description='Test if a stock has a strong business.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='only print stocks with a strong business')
    args = parser.parse_args()

    with open("tickers.txt", "r") as file:
        for line in file:
            symbol = line.strip()
            test_strong_business(symbol, args.verbose)


if __name__ == '__main__':
    main()
