# Python standard library
import re
import datetime
import sqlite3
import os 

# Third party
import asyncio

# Local
import news
import alphavantage

from gpt import get_gpt_opinion
from config import debug_mode, api_for_news, databases_path

# Dictionary for YES|NO|UNKNOWN answers
opinion_count = {
    'YES': 0,
    'NO': 0,
    'UNKNOWN': 0
}

def create_database():
    # Create dir if it doesn't exist
    if not os.path.exists(databases_path):
        os.makedirs(databases_path)

    conn = sqlite3.connect(f'{databases_path}/sentiments.db')  # Creates a connection to the SQLite database
    c = conn.cursor()  # Creates a cursor object

    # Creates the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS opinions
                 (time text, ticker text, headline text, opinion text)''')

    conn.close()  # Close the connection

def write_sentiment_to_db(ticker, sentiment):
    # Connect to the database
    conn = sqlite3.connect(f'{databases_path}/sentiments.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS sentiments
                 (date text, ticker text, sentiment integer)''')

    # Get the current date and time in YYYY-MM-DD HH:MM:SS format
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Insert the sentiment into the database
    c.execute("INSERT INTO sentiments VALUES (?, ?, ?)", (date, ticker, sentiment))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def get_hours_back():
    current_time = datetime.datetime.now()

    # Determine the number of hours to look back based on the current time
    if current_time.hour == 5:
        hours_back = 13  # Fetch news from 4:00 PM of the previous day
    elif current_time.hour == 6:
        hours_back = 1  # Fetch news from the last hour
    else:
        hours_back = 1  # Fetch news from the last hour
    return hours_back

async def get_headlines(ticker, overridehours_back=False):
    # Get headlines for ticker
    if debug_mode:
        headlines = ["Assessing Cardano’s chances of a bounce to $0.3", "Miners Send $1.67 Billion in Bitcoin to Binance"]
        ticker = 'BTC'
    else:
        if api_for_news == 'newsapi':
            headlines = await news.get_headlines_for_ticker(ticker)
        elif api_for_news == 'alphavantage':
            if overridehours_back:
                headlines = await alphavantage.get_headlines_for_ticker(ticker, 24)
            else:
                headlines = await alphavantage.get_headlines_for_ticker(ticker, get_hours_back())

async def get_opinions_for_ticker(ticker, overridehours_back=False):

    # Get current time
    current_time = datetime.datetime.now()

    # Get headlines for ticker
    headlines = await get_headlines(ticker, overridehours_back)

    # Get time for filename
    time = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    # No headlines found
    if headlines == None:
        return None
    
    # Create a list of tasks for each headline
    tasks = [get_gpt_opinion(headline, ticker, time) for headline in headlines]

    # Run all tasks concurrently and gather results
    opinions = await asyncio.gather(*tasks)

    return opinions

def get_sentiment_average(opinions):

    opinion_as_number = 0
    num_opinions = 0

    # Mapping of opinions to their corresponding actions
    opinion_mapping = {
        'YES': 1,
        'NO': -1,
        'UNKNOWN': 0,
    }

    # Go through opinions
    for opinion in opinions:
        # Extract using regex
        match = re.search(r'YES|NO|UNKNOWN', opinion)
        if match:
            # Get the opinion from the match
            opinion = match.group()
            # Add the corresponding action to opinion_as_number
            opinion_as_number += opinion_mapping.get(opinion, 0)
            num_opinions += 1

            # Increment the opinion count
            opinion_count[opinion] += 1

    # Calculate average if there are any opinions, else return 0
    if num_opinions > 0:
        return round(opinion_as_number / num_opinions, 3)
    else:
        return 0

def get_sentiment(number, ticker):

    # Return a string based on the value of number
    if number > 0.1:
        return f'Overall sentiment for {ticker} is positive.'
    elif number < -0.1:
        return f'Overall sentiment for {ticker} is negative.'
    else:
        return f'Overall sentiment for {ticker} is neutral.'

def print_sentiment(opinion_as_number, ticker):

    # Print the opinion with the sentiment
    print(f"Average value of opinions: {opinion_as_number}")
    print(f"YES: {opinion_count['YES']} | NO: {opinion_count['NO']} | UNKNOWN: {opinion_count['UNKNOWN']}")
    print(get_sentiment(opinion_as_number, ticker))