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

## What?

### Todo
* Add a comparison between similar stocks in Strong business tester
* Add a cheap business tester notebook
* Develop a guru stock idea notebook

### Done
* ~~Plot a graph for Free Cash Flow~~
* ~~Plot a graph for Balance sheet analysis~~
* ~~Try https://github.com/dpguthrie/yahooquery~~
* ~~Install JupyterLab for interactive and reproducible work~~
* ~~Install yfinance and pandas-datareader for yahoo finance API~~

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

## Challenges

* 2023-03-12 yfinance doesn't work after the first trial. It failed with the error "Exception: yfinance failed to
  decrypt Yahoo data response". The issue had been reported by others
  in https://github.com/ranaroussi/yfinance/issues/1407. Currently not solved yet.
