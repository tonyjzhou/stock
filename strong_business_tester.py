#!/usr/bin/env python

from datetime import datetime

from yahooquery import Ticker

from database import insert_data, read_data


def has_consecutive_positive_fcf(ticker):
    cash_flow = ticker.cash_flow(frequency='Annual')
    free_cash_flow = cash_flow[['asOfDate', 'FreeCashFlow']]
    free_cash_flow = free_cash_flow.set_index('asOfDate')
    fcf = free_cash_flow.to_dict()['FreeCashFlow']
    return all([v > 0 for v in fcf.values()])


def has_consistently_low_debt_ratios(debt_equity_ratio_values, threshold=2.4):
    return all([v < threshold for v in debt_equity_ratio_values])


def has_strong_balance_sheet(ticker):
    balance_sheet = ticker.balance_sheet(frequency='Quarterly')
    balance_sheet['TotalDebt/CommonStockEquity'] = balance_sheet['TotalDebt'] / balance_sheet['CommonStockEquity']
    debt_equity_ratio = balance_sheet[['asOfDate', 'TotalDebt/CommonStockEquity']]
    debt_equity_ratio = debt_equity_ratio.set_index('asOfDate').to_dict()['TotalDebt/CommonStockEquity']
    debt_equity_ratio_values = list(debt_equity_ratio.values())

    if not has_consistently_low_debt_ratios(debt_equity_ratio_values):
        print(f"{ticker.symbols} doesn't have consistently low debt ratios")
        return False

    return True


def has_processed(symbol):
    rows = read_data(symbol)
    if not rows:
        return False

    symbol, tested_at = rows[0]
    tested_at = datetime.strptime(tested_at, '%Y-%m-%d %H:%M:%S.%f')
    return (datetime.now() - tested_at).days < 365


def test_strong_business(symbol):
    if has_processed(symbol):
        print(f"{symbol} has already been processed")
        return False
    else:
        insert_data(symbol, datetime.now())

        ticker = Ticker(symbol)
        if not has_consecutive_positive_fcf(ticker):
            print(f"{ticker.symbols} doesn't have consecutive positive fcf")
            return False

        if not has_strong_balance_sheet(ticker):
            print(f"{ticker.symbols} doesn't have strong balance sheet")
            return False

        print(f"{ticker.symbols} has a strong business")
        return True


def main():
    with open("tickers.txt", "r") as file:
        for line in file:
            symbol = line.strip()  # Remove any trailing newline character
            test_strong_business(symbol)


if __name__ == '__main__':
    main()
