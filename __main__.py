import asyncio
import os
from sentiments import get_opinions_for_ticker, get_sentiment_average, write_sentiment_to_db, print_sentiment, create_database
from config import write_to_database
from trader import make_trading_decision

async def main():
    # Create the database
    if write_to_database:
        create_database()

    # If tickers.txt does not exist, create it
    if not os.path.exists('tickers.txt'):
        with open('tickers.txt', 'w') as f:
            f.write('TSLA\n')
            f.write('AAPL\n')
            f.write('GOOG\n')
            f.write('AMZN\n')
            f.write('MSFT\n')
            f.write('META\n')
            f.write('TSM\n')
            f.write('NVDA\n')
            f.write('JPM\n')

    # Get a list of tickers from as text file, row by row
    with open('tickers.txt') as f:
        tickers = f.read().splitlines()

    # Loop through all tickers
    for ticker in tickers:
        # Run the async function and get the result
        opinions = await get_opinions_for_ticker(ticker)

        if not opinions:
            continue

        # Process the opinions to get the sentiment
        num = get_sentiment_average(opinions)

        # Write the sentiment to the database
        if write_to_database:
            write_sentiment_to_db(ticker, num)

        # Print the sentiment
        print(f'Number of news headlines read: {len(opinions)}')
        print_sentiment(num, ticker)

        # Make a trading decision
        await make_trading_decision(ticker)

        # Add delay
        await asyncio.sleep(13)  # 12 seconds delay to stay within 5 requests per minute limit

# Run the main function
asyncio.run(main())