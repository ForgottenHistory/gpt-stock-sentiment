# Python standard library
import re
import datetime
import sqlite3

# Third party
import asyncio

# Local
import news
import alphavantage

from gpt import get_gpt_opinion
from config import debug_mode, api_for_news

# Dictionary for YES|NO|UNKNOWN answers
opinion_count = {
    'YES': 0,
    'NO': 0,
    'UNKNOWN': 0
}

def create_database():
    conn = sqlite3.connect('sentiments.db')  # Creates a connection to the SQLite database
    c = conn.cursor()  # Creates a cursor object

    # Creates the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS opinions
                 (time text, ticker text, headline text, opinion text)''')

    conn.close()  # Close the connection

def write_sentiment_to_db(ticker, sentiment):
    # Connect to the database
    conn = sqlite3.connect('sentiments.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS sentiments
                 (date text, ticker text, sentiment integer)''')

    # Get the current date
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Insert the sentiment into the database
    c.execute("INSERT INTO sentiments VALUES (?, ?, ?)", (date, ticker, sentiment))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

async def get_opinions_for_ticker(ticker):

    # Debug
    if debug_mode:
        headlines = ["Assessing Cardano’s chances of a bounce to $0.3", "Miners Send $1.67 Billion in Bitcoin to Binance"]
        ticker = 'BTC'
    else:
        if api_for_news == 'newsapi':
            # Get headlines for ticker
            headlines = await news.get_headlines_for_ticker(ticker)
        elif api_for_news == 'alphavantage':
            headlines = await alphavantage.get_headlines_for_ticker(ticker)

    # Get time for filename
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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
    print(f"Total value of opinions: {opinion_as_number}")
    print(f"YES: {opinion_count['YES']} | NO: {opinion_count['NO']} | UNKNOWN: {opinion_count['UNKNOWN']}")
    print(get_sentiment(opinion_as_number, ticker))