import finnhub

finnhub_client = finnhub.Client(api_key="cstluhpr01qj0ou20db0cstluhpr01qj0ou20dbg")

def symbol_lookup(params):
    return finnhub_client.symbol_lookup(params['company_name'])

def get_quote(symbol):
    return finnhub_client.quote(symbol)

def company_news(params):
    return finnhub_client.company_news(params['symbol'], _from=params['from_date'], to=params['to_date'])

def news_sentiment(symbol):
    return finnhub_client.news_sentiment(symbol)

def company_peers(symbol):
    return finnhub_client.company_peers(symbol)

def recommendation_trends(symbol):
    return finnhub_client.recommendation_trends(symbol)

def recommendation_trend(symbol):
    return finnhub_client.recommendation_trend(symbol)

def recommendation_earnings(symbol):
    return finnhub_client.recommendation_earnings(symbol)

def recommendation_insider(symbol):
    return finnhub_client.recommendation_insider(symbol)

def recommendation_insider_sentiment(symbol):
    return finnhub_client.recommendation_insider_sentiment(symbol)

def recommendation_insider_trading(symbol):
    return finnhub_client.recommendation_insider_trading(symbol)

def company_executive(symbol):
    return finnhub_client.company_executive(symbol)

def company_profile(symbol):
    return finnhub_client.company_profile2(symbol)

def company_profile2(symbol):
    return finnhub_client.company_profile2(symbol)

def index_constituents(symbol):
    return finnhub_client.index_constituents(symbol)

def index_profile(symbol):
    return finnhub_client.index_profile(symbol)

def index_constituents_exchanges(symbol):
    return finnhub_client.index_constituents_exchanges(symbol)

def index_constituents_prices(symbol):
    return finnhub_client.index_constituents_prices(symbol)

def index_constituents_profiles(symbol):
    return finnhub_client.index_constituents_profiles(symbol)

function_handler = {
    "symbol_lookup": symbol_lookup,
    "get_quote": get_quote,
    "company_news": company_news,
    "news_sentiment": news_sentiment,
}