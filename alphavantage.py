import requests
import os
import json

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

    # Save data to json file
    #with open('data.json', 'w') as f:
    #    json.dump(data, f)

    # Loop through all feed and get titles
    headlines = []
    for feed in data["feed"]:
        headlines.append(feed["title"])

    # Return headlines
    return headlines