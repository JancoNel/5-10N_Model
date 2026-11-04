import csv
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd
import yfinance as yf


TOP_N = 5
BACKTEST_START = "2019-01-01"
BACKTEST_END = None
WEIGHT_BY_MARKET_CAP = True

UNIVERSE_URL = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/"
    "master/data/constituents.csv"
)
PLOT_FILE = Path(__file__).with_name("backtest_returns.png")


def load_universe() -> list[str]:
    try:
        with urlopen(UNIVERSE_URL, timeout=30) as response:
            content = response.read().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise RuntimeError(
            f"Could not download the S&P 500 ticker list from {UNIVERSE_URL}"
        ) from error

    reader = csv.DictReader(StringIO(content))
    if not reader.fieldnames or "Symbol" not in reader.fieldnames:
        raise ValueError(f"The ticker list from {UNIVERSE_URL} has no Symbol column.")

    tickers = list(
        dict.fromkeys(
            row["Symbol"].strip().upper().replace(".", "-")
            for row in reader
            if row.get("Symbol") and row["Symbol"].strip()
        )
    )
    if not tickers:
        raise ValueError(f"The ticker list from {UNIVERSE_URL} is empty.")
    return tickers


def get_top_n_by_market_cap(
    tickers: list[str], n: int = TOP_N
) -> list[tuple[str, float]]:
    market_caps = []
    for ticker in tickers:
        market_cap = yf.Ticker(ticker).info.get("marketCap")
        if market_cap is not None and market_cap > 0:
            market_caps.append((ticker, float(market_cap)))
        else:
            print(f"Skipping {ticker}: Yahoo Finance did not provide a market cap.")

    top_n = sorted(market_caps, key=lambda item: item[1], reverse=True)[:n]
    if not top_n:
        raise ValueError("Yahoo Finance did not return market caps for any ticker.")
    return top_n


def calculate_weights(
    selected: list[tuple[str, float]], market_cap_weighted: bool
) -> pd.Series:
    tickers = [ticker for ticker, _ in selected]
    if market_cap_weighted:
        total_market_cap = sum(market_cap for _, market_cap in selected)
        values = [market_cap / total_market_cap for _, market_cap in selected]
    else:
        values = [1 / len(selected)] * len(selected)
    return pd.Series(values, index=tickers, dtype=float)


def download_prices(tickers: list[str]) -> pd.DataFrame:
    data = yf.download(
        tickers=tickers,
        start=BACKTEST_START,
        end=BACKTEST_END,
        auto_adjust=True,
        group_by="column",
        progress=False,
    )
    if data.empty or "Close" not in data:
        raise ValueError("Yahoo Finance returned no historical closing prices.")

    close = data["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(name=tickers[0])

    close = close.reindex(columns=tickers).dropna(axis="columns", how="all")
    missing = sorted(set(tickers) - set(close.columns))
    if missing:
        print(f"Skipping tickers with no historical prices: {', '.join(missing)}")
    if close.empty:
        raise ValueError("No selected ticker has historical closing prices.")
    return close


def backtest(prices: pd.DataFrame, weights: pd.Series) -> pd.Series:
    available_tickers = [
        ticker for ticker in weights.index if ticker in prices.columns
    ]
    prices = prices.loc[:, available_tickers].ffill().dropna()
    if prices.empty:
        raise ValueError("The selected tickers have no overlapping price history.")

    weights = weights.loc[available_tickers]
    weights = weights / weights.sum()
    normalized_prices = prices.div(prices.iloc[0])
    return normalized_prices.mul(weights, axis="columns").sum(axis="columns")


def plot_returns(portfolio_value: pd.Series, tickers: list[str]) -> None:
    cumulative_returns = portfolio_value - 1
    _, axis = plt.subplots(figsize=(11, 6))
    axis.plot(cumulative_returns.index, cumulative_returns, label="Portfolio")
    axis.set_title(f"Top {len(tickers)} Market-Cap Stocks: Cumulative Return")
    axis.set_xlabel("Date")
    axis.set_ylabel("Cumulative return")
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    axis.grid(True, alpha=0.3)
    axis.legend()
    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=150)
    print(f"Saved returns plot to {PLOT_FILE}")
    plt.show()


def main() -> None:
    universe = load_universe()
    print(f"Loaded {len(universe)} tickers.")

    selected = get_top_n_by_market_cap(universe)
    weights = calculate_weights(selected, WEIGHT_BY_MARKET_CAP)
    print("Selected stocks and portfolio weights:")
    for ticker, market_cap in selected:
        print(
            f"  {ticker}: {weights[ticker]:.1%} "
            f"(market cap ${market_cap:,.0f})"
        )

    prices = download_prices([ticker for ticker, _ in selected])
    available_weights = weights.loc[
        weights.index.intersection(prices.columns)
    ]
    portfolio_value = backtest(prices, available_weights)
    total_return = portfolio_value.iloc[-1] - 1
    print(
        f"Backtest period: {portfolio_value.index[0].date()} to "
        f"{portfolio_value.index[-1].date()}"
    )
    print(f"Portfolio return: {total_return:.2%}")
    plot_returns(portfolio_value, list(available_weights.index))


if __name__ == "__main__":
    main()
