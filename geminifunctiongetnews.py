from vertexai.generative_models import FunctionDeclaration

get_stock_price = FunctionDeclaration(
    name="get_stock_price",
    description="Fetch the current stock price of a given company",
    parameters={
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_company_overview = FunctionDeclaration(
    name="get_company_overview",
    description="Get company details and other financial data",
    parameters={
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_company_news = FunctionDeclaration(
    name="get_company_news",
    description="Get the latest news headlines for a given company.",
    parameters={
        "type": "object",
        "properties": {
            "tickers": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_news_with_sentiment = FunctionDeclaration(
    name="get_news_with_sentiment",
    description="Gets live and historical market news and sentiment data",
    parameters={
        "type": "object",
        "properties": {
            "news_topic": {
                "type": "string",
                "description": """News topic to learn about. Supported topics
                               include blockchain, earnings, ipo,
                               mergers_and_acquisitions, financial_markets,
                               economy_fiscal, economy_monetary, economy_macro,
                               energy_transportation, finance, life_sciences,
                               manufacturing, real_estate, retail_wholesale,
                               and technology""",
            },
        },
    },
)

