market_sentiment = dict(
    name="market_sentiment",
    description="Get the market sentiment for the company or stock",
    parameters={
        "type": "OBJECT",
        "properties": {
            "company_name": {
                "type": "STRING",
                "description": "Name of a company",
            },
        },
    },
)

monthly_stock_price = dict(
    name="monthly_stock_price",
    description="Get the monthly historical stock price for the company or symbol ",
    parameters={
        "type": "OBJECT",
        "properties": {
            "company_name": {
                "type": "STRING",
                "description": "Name of a company",
            },
        },
    },
)