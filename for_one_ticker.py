import asyncio
from sentiments import get_opinions_for_ticker, get_sentiment_average, write_sentiment_to_db, print_sentiment, create_database
from config import write_to_database

# Create the database
if write_to_database:
    create_database()

# Ask user for ticker
ticker = input('Enter ticker: ')

# Run the async function and get the result
opinions = asyncio.run(get_opinions_for_ticker(ticker))

# Process the opinions to get the sentiment
num = get_sentiment_average(opinions)

# Write the sentiment to the database
if write_to_database:
    write_sentiment_to_db(ticker, num)

# Print the sentiment
print(f'Number of news headlines read: {len(opinions)}')
print_sentiment(num, ticker)

print('Press enter to exit')
x = input()