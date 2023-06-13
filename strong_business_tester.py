#!/usr/bin/env python

from yahooquery import Ticker


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


def test_strong_business(ticker):
    if not has_consecutive_positive_fcf(ticker):
        print(f"{ticker.symbols} doesn't have consecutive positive fcf")
        return False

    if not has_strong_balance_sheet(ticker):
        print(f"{ticker.symbols} doesn't have strong balance sheet")
        return False

    print(f"{ticker.symbols} has a strong business")
    return True


def main():
    test_strong_business(Ticker('ABBV'))
    test_strong_business(Ticker('VZ'))
    test_strong_business(Ticker('AMGN'))
    test_strong_business(Ticker('EQNR'))
    test_strong_business(Ticker('BTI'))
    test_strong_business(Ticker('EL'))
    test_strong_business(Ticker('TGT'))
    test_strong_business(Ticker('JD'))
    test_strong_business(Ticker('MMM'))
    test_strong_business(Ticker('KDP'))
    test_strong_business(Ticker('D'))
    test_strong_business(Ticker('SYY'))
    test_strong_business(Ticker('DG'))
    test_strong_business(Ticker('NTR'))
    test_strong_business(Ticker('VOD'))
    test_strong_business(Ticker('WAT'))
    test_strong_business(Ticker('AMCR'))
    test_strong_business(Ticker('INCY'))
    test_strong_business(Ticker('NIO'))
    test_strong_business(Ticker('CF'))
    test_strong_business(Ticker('EPAM'))
    test_strong_business(Ticker('MOS'))
    test_strong_business(Ticker('DPZ'))
    test_strong_business(Ticker('IP'))
    test_strong_business(Ticker('RHI'))
    test_strong_business(Ticker('ICL'))
    test_strong_business(Ticker('VFC'))
    test_strong_business(Ticker('AA'))
    test_strong_business(Ticker('NFE'))
    test_strong_business(Ticker('CWEN'))


if __name__ == '__main__':
    main()
