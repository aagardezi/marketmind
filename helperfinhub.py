import finnhub
import helpercode
import logging

logger = logging.getLogger("MarketMind")

PROJECT_ID = helpercode.get_project_id()

finnhub_client = finnhub.Client(api_key=helpercode.access_secret_version(PROJECT_ID, "FinHubAccessKey"))

def symbol_lookup(params):
    return finnhub_client.symbol_lookup(params['company_name'])

def get_quote(params):
    return finnhub_client.quote(params['symbol'])

def company_news(params):
    return finnhub_client.company_news(params['symbol'], _from=params['from_date'], to=params['to_date'])

def news_sentiment(params):
    return finnhub_client.news_sentiment(params['symbol'])

def company_peers(params):
    return finnhub_client.company_peers(params['symbol'])

def insider_sentiment(params):
    return finnhub_client.stock_insider_sentiment(params['symbol'], params['from_date'], params['to_date'])

def company_basic_financials(params):
    return finnhub_client.company_basic_financials(params['symbol'],'all')

def financials_reported(params):
    return finnhub_client.financials_reported(symbol=params['symbol'], _from=params['from_date'], to=params['to_date'] )

def sec_filings(params):
    secfilings = finnhub_client.filings(symbol=params['symbol'], _from=params['from_date'], to=params['to_date'])
    parsed_filings = []
    for filing in secfilings:
        if filing['form'] in ['10-Q', '8-K']:
            parsed_filings.append({"accessNumber":filing['accessNumber'], 
                                   "symbol": params['symbol'], 
                                   "filedDate": filing['filedDate'],
                                   "report": helpercode.get_text_from_url(filing['reportUrl'])})
    
    return parsed_filings





#######################################################


def recommendation_trends(params):
    return finnhub_client.recommendation_trends(params['symbol'])

def recommendation_trend(params):
    return finnhub_client.recommendation_trend(params['symbol'])

def recommendation_earnings(params):
    return finnhub_client.recommendation_earnings(params['symbol'])

def recommendation_insider(params):
    return finnhub_client.recommendation_insider(params['symbol'])



def recommendation_insider_trading(params):
    return finnhub_client.recommendation_insider_trading(params['symbol'])

def company_executive(params):
    return finnhub_client.company_executive(params['symbol'])

def company_profile(params):
    return finnhub_client.company_profile2(symbol=params['symbol'])

def company_profile2(params):
    return finnhub_client.company_profile2(symbol=params['symbol'])

def index_constituents(params):
    return finnhub_client.index_constituents(params['symbol'])

def index_profile(params):
    return finnhub_client.index_profile(params['symbol'])

def index_constituents_exchanges(params):
    return finnhub_client.index_constituents_exchanges(params['symbol'])

def index_constituents_prices(params):
    return finnhub_client.index_constituents_prices(params['symbol'])

def index_constituents_profiles(params):
    return finnhub_client.index_constituents_profiles(params['symbol'])



function_handler = {
    "symbol_lookup": symbol_lookup,
    "get_quote": get_quote,
    "company_news": company_news,
    "company_profile": company_profile,
    "company_basic_financials": company_basic_financials,
    "company_peers": company_peers,
    "insider_sentiment": insider_sentiment,
    "financials_reported": financials_reported,
    "sec_filings": sec_filings,
}