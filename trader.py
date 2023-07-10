import sqlite3
import datetime
from datetime import datetime
from config import databases_path
from alphavantage import get_ticker_price

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

async def make_trading_decision(ticker):
    # Get the current sentiment score
    sentiment_score = get_current_sentiment(ticker)

    # Make trading decision based on the sentiment score
    if sentiment_score > 0:
        decision = 'BUY'
    elif sentiment_score < 0:
        decision = 'SELL'
    else:
        decision = 'HOLD'
    
    # Record the trading decision
    await record_trade_decision(ticker, decision)

    # Print the trading decision
    print(f'Trading decision for {ticker}: {decision}')

async def record_trade_decision(ticker, decision):
    # Connect to the database
    conn = sqlite3.connect(f'{databases_path}/trading_decisions.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS trading_decisions
        (timestamp text, ticker text, decision text, price real)
    ''')

    # Get the current timestamp in YYYY-MM-DD HH:MM:SS format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the current price of the ticker
    price = await get_ticker_price(ticker)

    # Record the trading decision
    c.execute('''
        INSERT INTO trading_decisions
        VALUES (?, ?, ?, ?)
    ''', (timestamp, ticker, decision, price))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Example usage
#ticker = input('Enter ticker: ')
#make_trading_decision(ticker)
