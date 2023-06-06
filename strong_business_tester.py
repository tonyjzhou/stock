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


def has_strong_business(ticker):
    if not has_consecutive_positive_fcf(ticker):
        print(f"{ticker.symbols} doesn't have consecutive positive fcf")
        return False

    if not has_strong_balance_sheet(ticker):
        print(f"{ticker.symbols} doesn't have strong balance sheet")
        return False

    print(f"{ticker.symbols} has a strong business")
    return True


def main():
    # has_strong_business(Ticker('TSLA'))
    # has_strong_business(Ticker('AAPL'))
    # has_strong_business(Ticker('LCID'))
    # has_strong_business(Ticker('AMZN'))
    # has_strong_business(Ticker('BABA'))

    has_strong_business(Ticker('ABBV'))
    has_strong_business(Ticker('VZ'))
    has_strong_business(Ticker('AMGN'))
    has_strong_business(Ticker('EQNR'))
    has_strong_business(Ticker('BTI'))
    has_strong_business(Ticker('EL'))
    has_strong_business(Ticker('TGT'))
    has_strong_business(Ticker('JD'))
    has_strong_business(Ticker('MMM'))
    has_strong_business(Ticker('KDP'))
    has_strong_business(Ticker('D'))
    has_strong_business(Ticker('SYY'))
    has_strong_business(Ticker('DG'))
    has_strong_business(Ticker('NTR'))
    has_strong_business(Ticker('VOD'))
    has_strong_business(Ticker('WAT'))
    has_strong_business(Ticker('AMCR'))
    has_strong_business(Ticker('INCY'))
    has_strong_business(Ticker('NIO'))
    has_strong_business(Ticker('CF'))
    has_strong_business(Ticker('EPAM'))
    has_strong_business(Ticker('MOS'))
    has_strong_business(Ticker('DPZ'))
    has_strong_business(Ticker('IP'))
    has_strong_business(Ticker('RHI'))
    has_strong_business(Ticker('ICL'))
    has_strong_business(Ticker('VFC'))
    has_strong_business(Ticker('AA'))
    has_strong_business(Ticker('NFE'))
    has_strong_business(Ticker('CWEN'))


if __name__ == '__main__':
    main()
