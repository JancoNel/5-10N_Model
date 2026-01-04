import yfinance as yf
import time
import os
 
# ----------------------------
# User-defined parameters
# Top N stocks to hold
TOP_N = 5
 
# Weighting per stock (percent)
i_first = 20
i_second = 20
i_third = 20
i_fourth = 20
i_five = 20
# Add more if TOP_N > 5
weight_vars = [i_first, i_second, i_third, i_fourth, i_five][:TOP_N]
 
# Files
UNIVERSE_FILE = "SP500.txt"
LAST_FILE = "last.txt"
 
# ----------------------------
def load_universe(file=UNIVERSE_FILE):
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} not found. Please provide SP500 tickers.")
    with open(file, "r") as f:
        tickers = [line.strip().upper() for line in f.readlines()]
    return tickers
 
# ----------------------------
def get_top_n_by_market_cap(tickers, n=TOP_N):
    market_caps = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            market_caps[ticker.upper()] = info.get('marketCap', 0)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            market_caps[ticker.upper()] = 0
    # Sort descending by market cap and pick top N
    top_n = sorted(market_caps.items(), key=lambda x: x[1], reverse=True)[:n]
    tickers_only = [t[0] for t in top_n]
    tickers_only.sort()  # Alphabetical
    return tickers_only
 
# ----------------------------
def read_last_file(filename=LAST_FILE):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        tickers = [line.strip().upper() for line in f.readlines()]
    tickers.sort()
    return tickers
 
def write_last_file(tickers, filename=LAST_FILE):
    with open(filename, "w") as f:
        for t in tickers:
            f.write(f"{t}\n")
 
# ----------------------------
# Main workflow
def main():
    universe = load_universe()
    print(f"Loaded universe of {len(universe)} tickers")
 
    while True:
        print("Fetching top N by market cap...")
        ArrNew = get_top_n_by_market_cap(universe, TOP_N)
        print("New top N:", ArrNew)
 
        ArrOld = read_last_file()
        print("Previous top N:", ArrOld)
 
        if ArrNew == ArrOld:
            print("No change in top N. Sleeping 24 hours...")
            time.sleep(24*60*60)  # Sleep for a day
            continue
        else:
            print("Top N changed. Rebalancing portfolio...")
 
            # ----------------------------
            # PLACEHOLDER: IBKR API SELL all ArrOld tickers
            for ticker in ArrOld:
                print(f"SELL all shares of {ticker} (placeholder)")
 
            # ----------------------------
            # PLACEHOLDER: Fetch account balance from IBKR
            account_balance = 100000  # Example: $100,000 cash
            print(f"Account balance: ${account_balance}")
 
            # Calculate dollar allocation per ticker based on weight_vars
            total_weight = sum(weight_vars)
            for ticker, weight in zip(ArrNew, weight_vars):
                allocation = (weight / total_weight) * account_balance
                print(f"BUY ${allocation:.2f} of {ticker} (placeholder)")
 
            # ----------------------------
            # Update last.txt
            write_last_file(ArrNew)
 
            print("Rebalance complete. Sleeping 24 hours...")
            time.sleep(24*60*60)  # Sleep for a day
 
# ----------------------------
if __name__ == "__main__":
    main()