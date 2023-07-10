import openai
import datetime
import os
import sqlite3
from config import openai_api_key, openai_model, print_opinions, write_to_database, databases_path

# Set up OpenAI API key
openai.api_key = openai_api_key

async def get_gpt_opinion(headline,ticker,time):
    
    # Define system and user messages
    system_prompt = """Forget all your previous instructions. Pretend you are a financial expert. You are
    a financial expert with stock recommendation experience. Answer “YES” if good 
    news, “NO” if bad news, or “UNKNOWN” if uncertain in the first line. Then
    elaborate with one short and concise sentence on the next line. Is this headline
    good or bad for the stock price of {} in the short term? Always write your response in English.
    Headline: {}""".format(ticker, headline)

    user_prompt = """Headline: {}""".format(headline)

    # Try catch as APIError can occur
    try:
        # Call OpenAI API
        completion = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
        )

        response = completion["choices"][0]["message"]["content"]

        # Write response to file
        if(write_to_database):
            write_db(response, ticker, time, headline)

        # Print response to console if print_opinions is enabled
        if(print_opinions):
            print_opinion(headline, response)

    # Catch errors
    except openai.error.APIError as e:
        print(f"An API error occurred: {e}")
        response = "API ERROR"
    except Exception as e:
        print(f"An error occurred: {e}")
        response = "ERROR"

    # Return the response, valid or not
    return response

def write_db(response, ticker, time, headline):
    # Connect to the database
    conn = sqlite3.connect(f'{databases_path}/opinions.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS opinions
                 (time text, ticker text, headline text, opinion text)''')

    # Insert the opinion into the database
    c.execute("INSERT INTO opinions VALUES (?, ?, ?, ?)", (time, ticker, headline, response))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def print_opinion(headline,response):

    # Print opinions to console
    print(f'Headline: {headline}')
    print(f'{response}\n\n')