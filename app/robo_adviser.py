from dotenv import load_dotenv
from pathlib import Path
import json
import os
import requests
from IPython import embed
import datetime

# Global variables to store parsed json
meta_data = {}
trading_data = []

def parse_response(response_text):
    response_json = json.loads(response_text)

    # Check if the response contains an error message returned from the api, if not continue with script
    try:
        error_message = response_json["Error Message"]
        quit("Sorry, we couldn't find any trading data for that stock symbol.")
    except KeyError as e:
        pass

    meta_data = response_json["Meta Data"]
    time_series_daily = response_json["Time Series (Daily)"]
    for daily_data in time_series_daily:
        #convert to easier dict
    
    return response_json

def write_prices_to_file():
    return

# Formats date into 'Month Day, Year'
def format_date(date_str):
    date_object = datetime.datetime.strptime(last_refreshed, '%Y-%m-%d')
    return date_object.strftime('%B %d, %Y')

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path) # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

# see: https://www.alphavantage.co/support/#api-key
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

symbol = input("Please input a stock symbol (e.g. 'MSFT'): ")

# Check if the symbol is an invalid type, if not continue with script
try:
    float(symbol)
    quit("Oh, expecting a properly-formed stock symbol like 'MSFT'. Please try again.")
except ValueError as e:
    pass

# see: https://www.alphavantage.co/documentation/#daily
# Assemble the request url to get daily data for the given stock symbol
request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
response = requests.get(request_url)
json_data = parse_response(response.text)

trading_data = json_data["Time Series (Daily)"]

last_refreshed = meta_data["3. Last Refreshed"]
latest_trading_data = trading_data[last_refreshed]
closing_price = float(latest_trading_data["4. close"])
latest_price_usd = round(closing_price, 2)

print(f"LATEST DAILY CLOSING PRICE FOR {symbol} IS: ${latest_price_usd}")
print(f"LATEST DATA FROM: {format_date(last_refreshed)}")
