# 5-10N_Model
- So this is a simple tradin

## Backtest

This project backtests a portfolio of the five largest companies by current
market capitalization. It downloads adjusted historical prices with yfinance,
calculates the portfolio's cumulative return, and displays and saves a plot as
`backtest_returns.png`.

The default weights are proportional to each selected company's market
capitalization within the top five. Set `WEIGHT_BY_MARKET_CAP` to `False` in
`main.py` to give each company an equal weight. Set `BACKTEST_START` and
`BACKTEST_END` there to change the date range; `BACKTEST_END = None` uses the
latest available data.

On Windows, run `setup.bat` to create and activate a virtual environment,
install requirements, and start the backtest:

```bat
setup.bat
```

Alternatively, install dependencies and run manually:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The S&P 500 ticker list is downloaded automatically from the
[datasets/s-and-p-500-companies](https://github.com/datasets/s-and-p-500-companies)
CSV when the script runs. Network access is required.

Yahoo Finance does not provide a complete historical series of market-cap
rankings through this simple workflow. Therefore, the current top five are
selected first and held over the full backtest period; this is not a
point-in-time historical simulation and may have survivorship/look-ahead bias.