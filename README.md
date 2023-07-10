# Stock

## Why?

To check if a stock is a worthy investment, I need to

1. compute a set of customized metrics for a stock
2. compare a stock with its peers

This project provides reusable components for it.

## How?

### Use virtual environment

```commandline
workon stock
```

### Install all packages

```commandline
pip install -r requirements.txt
```

### Run Jupyter Lab

```commandline
jupyter lab
```

### Run strong business tester

```commandline
./strong_business_tester.py
```

## What?

### Todo

1. Calculate volatility as 52-week high / 52-week low
2. Give a summary of all selected stocks with key metrics in a tabular format
3. ~~Eliminate companies with negative "Common Stock Equity"~~
4. Check if a business is cheap enough
    1. Compare Equity to Market Cap
    2. Compare average FCF to Market Cap
5. Check if a business is good
    1. ~~average FCF / average Equity >= x%~~
    2. Repurchase of Capital Stock
6. Don't store business that's strong but not cheap enough
7. Enable comparisons of multiple data sources: Yahoo Finance, https://www.macrotrends.net/ , https://www.barrons.com/
8. Add a comparison between similar stocks in Strong business tester
9. Make it a web application
10. Enable extracting data with the name of a company
    from https://www.barrons.com/market-data/stocks/new-fifty-two-week-highs-lows
11. When storing a company's symbol and the current datetime in the database, you could also store the results of the
    checks. This way, if you need to check a company's data again later, you can just query the database instead of
    having to fetch and process the data again.
12. Use multithreading or asynchronous programming to fetch and process data for multiple companies concurrently. This
    would be especially beneficial if the list of companies is large, as the program would not need to wait for each
    company's data to be fetched and processed before moving on to the next one.
13. Filter out OTC shares

### Done

* ~~Develop a guru stock idea notebook~~
* ~~Introduce a verbose option so that we only output those stock symbols with a strong business~~
* ~~Keep track of the list of companies that have already been processed in the past 12 months~~
    * ~~Create a stateful design~~
    * ~~Implement the stateful design~~
* ~~Process new stocks by reading an input file~~
* ~~Get a list of all US based companies~~
* ~~Add a cheap business tester~~
* ~~Add a cheap business tester notebook~~
* ~~Plot a graph for Free Cash Flow~~
* ~~Plot a graph for Balance sheet analysis~~
* ~~Try https://github.com/dpguthrie/yahooquery~~
* ~~Install JupyterLab for interactive and reproducible work~~
* ~~Install yfinance and pandas-datareader for yahoo finance API~~

### Challenges

* 2023-03-12 yfinance doesn't work after the first trial. It failed with the error "Exception: yfinance failed to
  decrypt Yahoo data response". The issue had been reported by others
  in https://github.com/ranaroussi/yfinance/issues/1407. Currently not solved yet.

### Questions

* ~~What fields do we need in the data model to keep the state for strong business tester?~~
    * symbol, tested_at
* ~~What are the possible database to use?~~
* ~~Should the data store be a graph or relational data store?~~

## Where?

### Jupyter Lab

* https://pypi.org/project/jupyterlab/

### yahooquery

* https://github.com/dpguthrie/yahooquery
* https://yahooquery.dpguthrie.com/

### yfinance

* https://github.com/ranaroussi/yfinance
* https://pypi.org/project/yfinance/
* https://aroussi.com/post/python-yahoo-finance
