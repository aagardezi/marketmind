from vertexai.generative_models import FunctionDeclaration

symbol_lookup = FunctionDeclaration(
    name="symbol_lookup",
    description="Get the symbol for accessing news data for a company",
    parameters={
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "Name of a company",
            },
        },
    },
)

company_news = FunctionDeclaration(
    name="company_news",
    description="Get the company news for the symbol supplied",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
            "from_date": {
                "type": "string",
                "description": "Start date for news data"
            },
            "to_date": {
                "type": "string",
                "description": "End date for news data"
            },
        },
        "required": [
            "symbol",
            "from_date",
            "to_date",
        ]
    },
)

company_profile = FunctionDeclaration(
    name="company_profile",
    description="Get the company profile for the symbol supplied",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
        },
    },
)

company_basic_financials = FunctionDeclaration(
    name="company_basic_financials",
    description="Get the company financials for the symbol supplied, Use it when doing a detaild analysis of a company",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
        },
    },
)

company_peers = FunctionDeclaration(
    name="company_peers",
    description="Get the list of peers for the symbol supplied",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
        },
    },
)

insider_sentiment = FunctionDeclaration(
    name="insider_sentiment",
    description="Get the insider sentiment for the symbol supplied to undersand if it is positive or negative",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
            "from_date": {
                "type": "string",
                "description": "Start date for insider sentiment data"
            },
            "to_date": {
                "type": "string",
                "description": "End date for insider sentiment data"
            },
        },
        "required": [
            "symbol",
            "from_date",
            "to_date",
        ]
    },
)

financials_reported = FunctionDeclaration(
    name="financials_reported",
    description="Get the financials reported for the symbol supplied",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
            "from_date": {
                "type": "string",
                "description": "Start date for insider sentiment data"
            },
            "to_date": {
                "type": "string",
                "description": "End date for insider sentiment data"
            },
        },
        "required": [
            "symbol",
            "from_date",
            "to_date",
        ]
    },
)

sec_filings = FunctionDeclaration(
    name="sec_filings",
    description="Get the SEC Filings reported for the symbol supplied",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol for the company",
            },
            "from_date": {
                "type": "string",
                "description": "Start date for insider sentiment data"
            },
            "to_date": {
                "type": "string",
                "description": "End date for insider sentiment data"
            },
        },
        "required": [
            "symbol",
            "from_date",
            "to_date",
        ]
    },
)