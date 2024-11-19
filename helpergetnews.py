import requests

API_KEY ="AXI03ZDK8WK2P060"

def get_stock_price_from_api(content):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={content['ticker']}&apikey={API_KEY}"
    api_request = requests.get(url)
    return api_request.text


def get_company_overview_from_api(content):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={content['ticker']}&apikey={API_KEY}"
    api_response = requests.get(url)
    return api_response.text


def get_company_news_from_api(content):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={content['tickers']}&limit=20&sort=RELEVANCE&apikey={API_KEY}"
    api_response = requests.get(url)
    return api_response.text


def get_news_with_sentiment_from_api(content):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={content['news_topic']}&limit=20&sort=RELEVANCE&apikey={API_KEY}"
    api_request = requests.get(url)
    return api_request.text

function_handler = {
    "get_stock_price": get_stock_price_from_api,
    "get_company_overview": get_company_overview_from_api,
    "get_company_news": get_company_news_from_api,
    "get_news_with_sentiment": get_news_with_sentiment_from_api,
}