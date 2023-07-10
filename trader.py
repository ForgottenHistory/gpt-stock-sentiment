import sqlite3
import datetime
from datetime import datetime

# Constants for market hours
MARKET_OPEN_HOUR = 6
MARKET_CLOSE_HOUR = 16

def get_current_sentiment(ticker):
    # Connect to the database
    conn = sqlite3.connect('sentiments.db')
    c = conn.cursor()

    # Get the current date and time
    now = datetime.now()

    # Get the sentiment scores from the database based on the time
    if now.hour < MARKET_OPEN_HOUR:
        c.execute(f"SELECT sentiment FROM sentiments WHERE ticker='{ticker}' AND date>=datetime('now', '-1 day')")
    elif now.hour < MARKET_CLOSE_HOUR:
        c.execute(f"SELECT sentiment FROM sentiments WHERE ticker='{ticker}' AND date>=datetime('now', 'start of day')")
    else:
        c.execute(f"SELECT sentiment FROM sentiments WHERE ticker='{ticker}' AND date>=datetime('now', '-1 day', 'start of day')")

    # Get the sentiment scores
    sentiment_scores = c.fetchall()

    # Close the connection
    conn.close()

    # Return the average sentiment score
    return sum(score for score, in sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

def make_trading_decision(ticker):
    # Get the current sentiment score
    sentiment_score = get_current_sentiment(ticker)

    # Make trading decision based on the sentiment score
    if sentiment_score > 0:
        print(f"Buy {ticker}")
    elif sentiment_score < 0:
        print(f"Short {ticker}")
    else:
        print(f"Hold {ticker}")

# Example usage
ticker = input('Enter ticker: ')
make_trading_decision(ticker)
