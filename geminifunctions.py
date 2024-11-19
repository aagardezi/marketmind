from vertexai.generative_models import FunctionDeclaration

BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = "genaillentsearch"

list_datasets_func = FunctionDeclaration(
    name="list_datasets",
    description="Get a list of datasets that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {},
    },
)

list_tables_func = FunctionDeclaration(
    name="list_tables",
    description="List tables in a dataset that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {
            "dataset_id": {
                "type": "string",
                "description": "Dataset ID to fetch tables from.",
            }
        },
        "required": [
            "dataset_id",
        ],
    },
)

get_table_func = FunctionDeclaration(
    name="get_table",
    description="Get information about a table, including the description, schema, and number of rows that will help answer the user's question. Always use the fully qualified dataset and table names.",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified ID of the table to get information about",
            }
        },
        "required": [
            "table_id",
        ],
    },
)

sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Get information from data in BigQuery using SQL queries",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": f"""SQL query on a single line that will help give quantitative answers to the user's question when run on a BigQuery dataset and table. In the SQL query, always use the fully qualified dataset and table names.
                When writing SQL query ensure you use the Date_Time field in the where clause. {PROJECT_ID}.{BIGQUERY_DATASET_ID}.lse_normalised table is the main trade table
                RIC is the column to search for a stock""",
            }
        },
        "required": [
            "query",
        ],
    },
)


# get_stock_price = FunctionDeclaration(
#     name="get_stock_price",
#     description="Fetch the current stock price of a given company",
#     parameters={
#         "type": "object",
#         "properties": {
#             "ticker": {
#                 "type": "string",
#                 "description": "Stock ticker symbol for a company",
#             }
#         },
#     },
# )

# get_company_overview = FunctionDeclaration(
#     name="get_company_overview",
#     description="Get company details and other financial data",
#     parameters={
#         "type": "object",
#         "properties": {
#             "ticker": {
#                 "type": "string",
#                 "description": "Stock ticker symbol for a company",
#             }
#         },
#     },
# )

# get_company_news = FunctionDeclaration(
#     name="get_company_news",
#     description="Get the latest news headlines for a given company.",
#     parameters={
#         "type": "object",
#         "properties": {
#             "tickers": {
#                 "type": "string",
#                 "description": "Stock ticker symbol for a company",
#             }
#         },
#     },
# )

# get_news_with_sentiment = FunctionDeclaration(
#     name="get_news_with_sentiment",
#     description="Gets live and historical market news and sentiment data",
#     parameters={
#         "type": "object",
#         "properties": {
#             "news_topic": {
#                 "type": "string",
#                 "description": """News topic to learn about. Supported topics
#                                include blockchain, earnings, ipo,
#                                mergers_and_acquisitions, financial_markets,
#                                economy_fiscal, economy_monetary, economy_macro,
#                                energy_transportation, finance, life_sciences,
#                                manufacturing, real_estate, retail_wholesale,
#                                and technology""",
#             },
#         },
#     },
# )

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
    description="Get the symbol for accessing news data for a company",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Name of a company",
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