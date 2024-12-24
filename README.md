# Stock Analysis Project

## Overview
This Python-based project is designed to assess the financial health and strength of businesses by analyzing key financial metrics. It leverages various scripts and Jupyter notebooks to fetch financial data from sources like `yahooquery` and `yfinance`, evaluate the strength of businesses based on criteria such as positive free cash flow, good return on equity, strong balance sheet, and low debt ratios, and output the analysis in a structured format.

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
  - [Database Management](#database-management)
  - [Financial Analysis](#financial-analysis)
  - [Testing and Refreshing Data](#testing-and-refreshing-data)
- [Key Functionalities](#key-functionalities)
- [Interactive Notebooks](#interactive-notebooks)
- [Dependencies](#dependencies)
- [Contributing](#contributing)

## Setup
Ensure Python is installed on your system. Follow these steps to set up the project:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/stock-analysis-project.git
   cd stock-analysis-project
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Database Management
`database.py` handles all database operations, supporting the storage, retrieval, and management of analysis results. It uses `aiosqlite` for asynchronous database interactions.

- **Refresh the Database:**
  This will clear existing data from the database based on the symbols listed in `tickers.txt`.
  ```bash
  python database.py
  ```

- **Test Database Operations:**
  Uncomment the `test_run()` function call in `database.py` to perform a test of insert, read, update, and delete operations.
  ```python
  if __name__ == '__main__':
      # asyncio.run(test_run())
      asyncio.run(refresh())
  ```

### Financial Analysis
`strong_business_tester.py` identifies strong businesses by analyzing financial data. The script evaluates companies based on multiple financial health indicators, including consistent positive free cash flow and return on equity above a certain threshold.

- **Run the Financial Analyzer:**
  ```bash
  python strong_business_tester.py -v
  ```
  This command runs the script in verbose mode, printing detailed information about each company analyzed and indicating whether it is considered a strong business.

### Testing and Refreshing Data
The project includes several Jupyter notebooks for testing and data visualization. These notebooks can be used to interactively explore financial data and results.

- **Run the Notebooks:**
  Open any notebook with JupyterLab:
  ```bash
  jupyter lab
  ```

## Key Functionalities
- **Free Cash Flow Analysis:** Determines if a company has had consecutive years of positive free cash flow, excluding businesses with inconsistent FCF like Amazon and MU.
  
- **Return on Equity (ROE) Evaluation:** Calculates the average ROE and assesses if it is above a certain threshold, indicating efficient use of equity.
  
- **Balance Sheet Strength:** Analyzes the balance sheet for a strong equity position and consistently low debt ratios.
  
- **Debt/Equity Ratio Analysis:** Evaluates the company's debt relative to its equity to assess financial leverage.
  
- **Market Volatility:** (Commented out in the current version) Evaluates the stock's volatility based on its 52-week low and high prices.

## Interactive Notebooks
Explore the `jupyter` directory for Jupyter notebooks that provide examples of data fetching, analysis, and visualization. Some notable notebooks include:

- **strong_business_tester_Moderna.ipynb:** Analyzes financial data for Moderna.
- **hello_yfinance.ipynb:** Demonstrates basic usage of the `yfinance` library.
- **strong_business_tester_Adobe.ipynb:** Analyzes financial data for Adobe.
- **example_plot.ipynb:** Provides examples of plotting financial data using Matplotlib and Pandas.
- **strong_business_tester_BlackRock.ipynb:** Analyzes financial data for BlackRock.
- **strong_business_tester_CBUMF.ipynb:** Analyzes financial data for CBUMF.
- **strong_business_tester_tesla.ipynb:** Analyzes financial data for Tesla.
- **strong_business_tester_Block.ipynb:** Analyzes financial data for Block.

Open these notebooks with JupyterLab:
```bash
jupyter lab
```


## Dependencies
The project relies on the following Python packages:
- **JupyterLab:** For interactive notebooks.
- **yahooquery:** To fetch financial data from Yahoo Finance.
- **yfinance:** For additional financial data retrieval.
- **pandas-datareader:** To access financial data.
- **matplotlib:** For data visualization.
- **tabulate:** To display data in tabular format.
- **aiosqlite:** For asynchronous SQLite database operations.

Install all dependencies using:
```bash
pip install -r requirements.txt
```


## Contributing
Contributions are welcome! Follow these steps to contribute:

1. **Fork the repository.**
2. **Create a new branch:**
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. **Make your changes and commit them:**
   ```bash
   git commit -m "Add your detailed description of the feature"
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature/YourFeatureName
   ```
5. **Open a pull request.**

Please ensure your code adheres to the project's coding standards and includes appropriate tests.
