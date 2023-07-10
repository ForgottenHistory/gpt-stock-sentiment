import os

# Important
api_for_news = "alphavantage" # "newsapi" or "alphavantage"

# OpenAI API
# https://platform.openai.com
openai_api_key = os.getenv('OPENAI_API_KEY')
#openai_model = 'gpt-4'
openai_model = 'gpt-3.5-turbo'

# News API
# newsapi.org
newsapi_api_key = os.getenv('NEWS_API_KEY')
newsapi_sort_by = 'relevancy'
newsapi_language = 'en'
from_days_ago = 1 # Number of days ago to get headlines from. Higher values need a paid plan

# Alpha Vantage
# https://www.alphavantage.co
alpha_vantage_api_key = os.getenv('ALPHAVANTAGE_API_KEY')

# Miscellanous
print_opinions = True # Will print opinion as they are generated
write_to_database = True # Will write headlines, opinions and sentiment to databases
debug_mode = False # Will replace headlines with debug headlines to avoid API calls