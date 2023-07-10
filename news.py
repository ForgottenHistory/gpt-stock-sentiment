import sqlite3
import datetime
import asyncio
from config import newsapi_api_key, write_to_database, newsapi_language, newsapi_sort_by, from_days_ago, databases_path
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key=newsapi_api_key)

async def get_headlines_for_ticker(ticker):

    # Get yesterday's date (year-month-day)
    fromParam = datetime.datetime.now() - datetime.timedelta(days=from_days_ago)
    fromParam = fromParam.strftime("%Y-%m-%d")
    
    # Use the NewsApiClient to get the headlines
    all_articles = newsapi.get_everything(q=ticker,
                                          language=newsapi_language,
                                          sort_by=newsapi_sort_by,
                                          from_param=fromParam,)
    
    # Extract the headlines from the articles
    headlines = [article['title'] for article in all_articles['articles']]

    # Write the headlines to the database
    if write_to_database:
        write_db(headlines, ticker)

    return headlines

def write_db(headlines, ticker):
    # Connect to the database
    conn = sqlite3.connect(f'{databases_path}/headlines.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS headlines
                 (time text, ticker text, headline text)''')

    # Get the current time
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert each headline into the database
    for headline in headlines:
        c.execute("INSERT INTO headlines VALUES (?, ?, ?)", (time, ticker, headline))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Run get_headlines_for_ticker() for 'BTC' with asyncio
asyncio.run(get_headlines_for_ticker('BTC'))