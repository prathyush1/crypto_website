import requests
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch historical Bitcoin price data for a given timestamp
def fetch_bitcoin_price_history(timestamp):
    base_url = "https://min-api.cryptocompare.com/data/v2/histohour"
    
    # CryptoCompare API parameters
    params = {
        "fsym": "BTC",
        "tsym": "USD",
        "limit": 2000, # Maximum number of data points allowed per request
        "toTs": timestamp,
        "api_key": "YOUR_API_KEY" # Replace with your CryptoCompare API key
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()["Data"]["Data"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df
    else:
        print("Error fetching data:", response.status_code)
        return None

# Define the date range for fetching data
end_date = datetime.now()
start_date = end_date - timedelta(days=4*365)

# Fetch historical Bitcoin price data
bitcoin_price_history = pd.DataFrame()

while end_date > start_date:
    timestamp = int(end_date.timestamp())
    df = fetch_bitcoin_price_history(timestamp)
    
    if df is not None:
        bitcoin_price_history = pd.concat([df, bitcoin_price_history], ignore_index=True)
        end_date = df.iloc[0]["time"] - timedelta(hours=1)
    else:
        print("Error fetching data")
        break

# Display historical Bitcoin price data
print(bitcoin_price_history)

import numpy as np

# 1) First date of available data
first_date = bitcoin_price_history['time'].min()
print(f"First date of available data: {first_date}")

# 2) Number of days of available data
num_days = (bitcoin_price_history['time'].max() - first_date).days + 1
print(f"Number of days of available data: {num_days}")

# 3) Dates with missing data points
date_counts = bitcoin_price_history['time'].dt.date.value_counts().sort_index()
missing_dates = date_counts[date_counts != 24].index.tolist()
print(f"Dates with missing data points: {len(missing_dates)}")
print("Dates:")
for date in missing_dates:
    print(f"  {date} (data points: {date_counts[date]})")

# 4) Records with missing values
num_missing_records = bitcoin_price_history.isnull().any(axis=1).sum()
print(f"Number of records with missing values: {num_missing_records}")

# Trading Strategy: Moving Average Crossover
bitcoin_price_history['position'] = np.where(bitcoin_price_history['close'] > bitcoin_price_history['sma'], 1, -1)

# Calculate Returns
bitcoin_price_history['returns'] = bitcoin_price_history['close'].pct_change()
bitcoin_price_history['strategy_returns'] = bitcoin_price_history['returns'] * bitcoin_price_history['position'].shift(1)

# Calculate Cumulative Returns
bitcoin_price_history['cumulative_returns'] = np.exp(np.log1p(bitcoin_price_history['returns']).cumsum())
bitcoin_price_history['cumulative_strategy_returns'] = np.exp(np.log1p(bitcoin_price_history['strategy_returns']).cumsum())

# Estimate Performance
start_date = datetime.now() - timedelta(days=365)
performance = bitcoin_price_history[bitcoin_price_history['time'] >= start_date][['cumulative_returns', 'cumulative_strategy_returns']].iloc[-1] - 1

print(f"Buy and Hold Strategy Return: {performance['cumulative_returns'] * 100:.2f}%")
print(f"Moving Average Crossover Strategy Return: {performance['cumulative_strategy_returns'] * 100:.2f}%")

# Calculate the timestamp for exactly one year ago
one_year_ago = datetime.now() - timedelta(days=365)

# Find the nearest timestamp in the dataset
nearest_timestamp = bitcoin_price_history.iloc[(bitcoin_price_history['time'] - one_year_ago).abs().idxmin()]

# Extract the price of Bitcoin for exactly one year ago
price_one_year_ago = nearest_timestamp['close']

print(f"Price of Bitcoin exactly one year ago: ${price_one_year_ago:.2f}")

# Define the start and end dates for each year
start_date = bitcoin_price_history['time'].min()
end_date = bitcoin_price_history['time'].max()
years = int((end_date - start_date).days / 365) + 1

# Analyze each year
for i in range(years):
    year_start = start_date + timedelta(days=i*365)
    year_end = start_date + timedelta(days=(i+1)*365)

    # Filter data for the current year and create a copy
    yearly_data = bitcoin_price_history[(bitcoin_price_history['time'] >= year_start) & (bitcoin_price_history['time'] < year_end)].copy()

    # Calculate buy and sell orders
    buy_orders = (yearly_data['position'] == 1).sum()
    sell_orders = (yearly_data['position'] == -1).sum()

    # Calculate total returns for the year
    total_returns = yearly_data['strategy_returns'].sum()

    # Calculate median profit/loss per buy-sell order pair
    yearly_data['trade_returns'] = yearly_data['strategy_returns'] * yearly_data['position']
    median_trade_returns = yearly_data['trade_returns'][yearly_data['trade_returns'] != 0].median()

    # Display the results
    print(f"Year {i+1}:")
    print(f"  Buy Orders: {buy_orders}")
    print(f"  Sell Orders: {sell_orders}")
    print(f"  Total Returns: {total_returns * 100:.2f}%")
    print(f"  Median Profit/Loss per Buy-Sell Order Pair: {median_trade_returns * 100:.2f}%")

    # Buy and hold strategy
    buy_and_hold_returns = yearly_data['returns'].sum()
    print(f"  Buy and Hold Strategy Returns: {buy_and_hold_returns * 100:.2f}%")



