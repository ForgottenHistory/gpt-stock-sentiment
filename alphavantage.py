import requests
from datetime import datetime, timedelta
from config import alpha_vantage_api_key

api_key = alpha_vantage_api_key

async def get_headlines_for_ticker(ticker):

    # Get date and time in format YYYYMMDDTHHMM (e.g. 20210909T0000)
    date = datetime.now() - timedelta(days=1)
    date = date.strftime('%Y%m%dT0000')

    # Create url for ticker
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}&sort=LATEST&time_from={date}'
    
    # Send request and get data as json
    r = requests.get(url)
    data = r.json()

    # Check for invalid input
    # {'Information': 'Invalid inputs. Please refer to the API documentation https://www.alphavantage.co/documentation#newsapi and try again.'}
    if 'Information' in data:
        return []

    # Loop through all feed and get titles
    headlines = []
    for feed in data["feed"]:
        headlines.append(feed["title"])

    # Return headlines
    return headlines

def get_ticker_price(ticker):
    # Create url for ticker
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}'

    # Send request and get data as json
    r = requests.get(url)
    data = r.json()

    print(data)

    # Check for invalid input
    # {'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency.'}
    if 'Note' in data:
        return 0

    # Get the price
    price = float(data["Global Quote"]["05. price"])

    return price

print(get_ticker_price('AAPL'))