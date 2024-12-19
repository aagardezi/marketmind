import requests
import helpercode
import logging

logger = logging.getLogger("MarketMind")

PROJECT_ID = helpercode.get_project_id()

api_key=helpercode.access_secret_version(PROJECT_ID, "AlphaVantageKey")

def monthly_stock_price(params):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={params['symbol']}&apikey={api_key}"
    r = requests.get(url)
    return r.json()

def market_sentiment(params):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&symbol={params['symbol']}&apikey={api_key}"
    r = requests.get(url)
    return r.json()

function_handler = {
    "monthly_stock_price": monthly_stock_price,
    "market_sentiment": market_sentiment,
}