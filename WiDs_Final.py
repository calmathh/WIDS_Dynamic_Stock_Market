import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create short simple moving average
    signals['short_mavg'] = data['Close'].rolling(window=40, min_periods=1, center=False).mean()

    # Create long simple moving average
    signals['long_mavg'] = data['Close'].rolling(window=100, min_periods=1, center=False).mean()

    # Create signals
    signals['signal'][40:] = np.where(signals['short_mavg'][40:] > signals['long_mavg'][40:], 1.0, 0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    return signals

def execute_trades(signals):
    buys = signals[signals['positions'] == 1.0].index
    sells = signals[signals['positions'] == -1.0].index

    return buys, sells

def backtest(data, signals):
    initial_capital = 100000.0
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    portfolio = pd.DataFrame(index=signals.index).fillna(0.0)

    positions['stock'] = 100 * signals['signal']   # Buy 100 shares
    portfolio['positions'] = positions.multiply(data['Close'], axis=0)
    portfolio['cash'] = initial_capital - (positions.diff().multiply(data['Close'], axis=0)).cumsum()

    portfolio['total'] = portfolio['positions'] + portfolio['cash']
    portfolio['returns'] = portfolio['total'].pct_change()

    return portfolio

if __name__ == "__main__":
    nifty50_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'BAJAJ-AUTO', 'HDFC', 'LT', 'TCS', 'TATASTEEL', 'MARUTI', 'ONGC', 'KOTAKBANK', 'LT', 'HCLTECH', 'WIPRO', 'AXISBANK', 'POWERGRID', 'BPCL', 'ONGC', 'COALINDIA', 'HEROMOTOCO', 'CIPLA', 'NESTLEIND', 'MARUTI', 'ULTRACEMCO', 'SBIN', 'BAJFINANCE', 'ADANIPORTS', 'SUNPHARMA', 'ITC', 'BHARTIARTL', 'NTPC', 'JSWSTEEL', 'M&M', 'GRASIM', 'EICHERMOT', 'IOC', 'TECHM', 'SHREECEM', 'TITAN', 'ASIANPAINT', 'DRREDDY', 'NTPC', 'TATASTEEL']

    start_date = '2022-01-01'
    end_date = '2023-01-01'

    for symbol in nifty50_symbols:
        print(f"\nAnalyzing {symbol}...")

        # Fetch data
        data = fetch_data(symbol, start_date, end_date)

        # Check if data is empty
        if data.empty:
            print(f"No data available for {symbol}. Skipping...")
            continue

        # Generate signals
        signals = generate_signals(data)
        buys, sells = execute_trades(signals)

        # Backtest
        portfolio = backtest(data, signals)

        print("Buy signals at:", buys)
        print("Sell signals at:", sells)
        print(portfolio.tail())  # Print the last few rows of the portfolio for each stock
