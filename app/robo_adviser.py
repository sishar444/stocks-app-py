from dotenv import load_dotenv
from pathlib import Path
import json
import os
import requests
from IPython import embed
import datetime
import csv

def parse_response(response_text):
    response_json = json.loads(response_text)

    # Check if the response contains an error message returned from the api, if not continue with script
    try:
        # Quit script with message
        error_message = response_json["Error Message"]
        quit("Sorry, we couldn't find any trading data for that stock symbol.")
    except KeyError as e:
        pass

    results = []
    time_series_daily = response_json["Time Series (Daily)"]
    for trading_date in time_series_daily:
        prices_data = time_series_daily[trading_date]
        result = {
            "date": trading_date,
            "open": prices_data["1. open"],
            "high": prices_data["2. high"],
            "low": prices_data["3. low"],
            "close": prices_data["4. close"],
            "volume": prices_data["5. volume"]
        }
        results.append(result)

    return results

def write_prices_to_file(prices = [], filename = "data/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for data in prices:
            row = {
                "timestamp": data["date"],
                "open": data["open"],
                "high": data["high"],
                "low": data["low"],
                "close": data["close"],
                "volume": data["volume"]
            }
            writer.writerow(row)

# Formats date into 'Month Day, Year'
def format_date(date_time_object):
    return date_time_object.strftime('%B %d, %Y')

# Formats date into 'Month Day, Year'
def format_date_string(date_str):
    date_object = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return date_object.strftime('%B %d, %Y')

def format_date_time(date_time):
    return date_time.strftime("%I:%M %p")

def latest_closing_price(latest_prices):
    closing_price = float(latest_prices["close"])
    closing_price_formatted = round(closing_price, 2)
    return closing_price_formatted

def recent_high_price(prices_data):
    high_prices = []
    for prices in prices_data:
        high_price = float(prices["high"])
        high_prices.append(high_price)

    max_price = max(high_prices)
    max_price_formatted = round(max_price, 2)
    return max_price_formatted

def recent_low_price(prices_data):
    low_prices = []
    for prices in prices_data:
        low_price = float(prices["low"])
        low_prices.append(low_price)

    min_price = min(low_prices)
    min_price_formatted = round(min_price, 2)
    return min_price_formatted

def stock_recommendation(latest_closing_price, recent_low_price):
    price_diff = latest_closing_price/recent_low_price
    if price_diff > 1.2:
        return "BUY"
    else:
        return "DON'T BUY"

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path) # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

# see: https://www.alphavantage.co/support/#api-key
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

symbol = input("Please input a stock symbol (e.g. 'MSFT'): ")

# Check if the symbol is an invalid type, if not continue with script
try:
    # Quit script with message
    float(symbol)
    quit("Oh, expecting a properly-formed stock symbol like 'MSFT'. Please try again.")
except ValueError as e:
    pass

# see: https://www.alphavantage.co/documentation/#daily
# Assemble the request url to get daily data for the given stock symbol
request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
response = requests.get(request_url)

# Parse Response
json_data = parse_response(response.text)

# Write to CSV file
write_prices_to_file(prices=json_data, filename="data/prices.csv")

# Perform Calculations
latest_price_usd = latest_closing_price(json_data[0])
recent_high_price_usd = recent_high_price(json_data)
recent_low_price_usd = recent_low_price(json_data)
last_refreshed = format_date_string(json_data[0]["date"])

current_datetime = datetime.datetime.now()
run_at_time = format_date_time(current_datetime.time())
run_at_date = format_date(current_datetime)

print(f"STOCK: {symbol}")
print(f"RUN AT: {run_at_time} ON {run_at_date}")
print(f"LATEST DATA FROM: {last_refreshed}")
print(f"LATEST DAILY CLOSING PRICE FOR {symbol} IS: ${'{:,.2f}'.format(latest_price_usd)}")
print(f"RECENT AVERAGE HIGH PRICE FOR {symbol} IS: ${'{:,.2f}'.format(recent_high_price_usd)}")
print(f"RECENT AVERAGE LOW PRICE FOR {symbol} IS: ${'{:,.2f}'.format(recent_low_price_usd)}")

# Final Recommendation
recommendation = stock_recommendation(latest_price_usd, recent_low_price_usd)
more_or_less = ""
if recommendation == "BUY":
    more_or_less = "MORE"
else:
    more_or_less = "LESS"
print(f"RECOMMENDATION: {recommendation}")
print(f"WE RECOMMEND TO {recommendation} BECAUSE THE LATEST CLOSING PRICE FOR {symbol} IS {more_or_less} THAN 20% ABOVE ITS RECENT AVERAGE LOW PRICE.")
