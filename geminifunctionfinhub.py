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