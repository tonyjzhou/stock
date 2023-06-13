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
    if read_data(symbol):
        return True
    return False


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
    test_strong_business('ABBV')
    test_strong_business('VZ')
    test_strong_business('AMGN')
    test_strong_business('EQNR')
    test_strong_business('BTI')
    test_strong_business('EL')
    test_strong_business('TGT')
    test_strong_business('JD')
    test_strong_business('MMM')
    test_strong_business('KDP')
    test_strong_business('D')
    test_strong_business('SYY')
    test_strong_business('DG')
    test_strong_business('NTR')
    test_strong_business('VOD')
    test_strong_business('WAT')
    test_strong_business('AMCR')
    test_strong_business('INCY')
    test_strong_business('NIO')
    test_strong_business('CF')
    test_strong_business('EPAM')
    test_strong_business('MOS')
    test_strong_business('DPZ')
    test_strong_business('IP')
    test_strong_business('RHI')
    test_strong_business('ICL')
    test_strong_business('VFC')
    test_strong_business('AA')
    test_strong_business('NFE')
    test_strong_business('CWEN')


if __name__ == '__main__':
    main()
