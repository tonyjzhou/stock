# Stock Analysis Project

## Overview
This Python-based project is designed to assess the financial health and strength of businesses by analyzing key financial metrics. It employs a script that fetches financial data from `yahooquery`, evaluates the strength of businesses based on criteria such as positive free cash flow, good return on equity, strong balance sheet, and low debt ratios, and outputs the analysis in a structured format.

## Setup
Ensure Python is installed on your system and install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
### Database Management
`database.py` handles database operations, supporting the storage and retrieval of analysis results.

### Financial Analysis
`strong_business_tester.py` identifies strong businesses by analyzing financial data. The script evaluates companies based on multiple financial health indicators, including consistent positive free cash flow and return on equity above a certain threshold. To use this script:
```
python strong_business_tester.py -v
```
This command runs the script in verbose mode, printing detailed information about each company analyzed and indicating whether it is considered a strong business.

### Key Functionalities
- **Free Cash Flow Analysis**: Determines if a company has had consecutive years of positive free cash flow, excluding businesses like Amazon and MU for having negative FCF in some years.
- **Return on Equity (ROE) Evaluation**: Calculates the average ROE and assesses if it is above a certain threshold, indicating efficient use of equity.
- **Balance Sheet Strength**: Analyzes the balance sheet for a strong equity position and consistently low debt ratios.
- **Market Volatility**: (Commented out in the current version) Evaluates the stock's volatility based on its 52-week low and high prices.

### Interactive Notebooks
Explore the `jupyter` directory for Jupyter notebooks that provide examples of data fetching, analysis, and visualization. Open these notebooks with JupyterLab:
```
jupyter lab
```

## Dependencies
- JupyterLab
- yahooquery
- yfinance
- pandas-datareader
- matplotlib
- tabulate

## Contributing
Contributions are welcome. Feel free to fork the repository, make improvements, and submit a pull request.