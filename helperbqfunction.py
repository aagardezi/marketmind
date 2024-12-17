import streamlit as st
from google.cloud import bigquery
import logging

logger = logging.getLogger("MarketMind")

BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = "genaillentsearch"


def list_datasets(client, params):
    api_response = client.list_datasets()
    api_response = BIGQUERY_DATASET_ID
    logger.warning(api_response)
    # api_response = str([dataset.dataset_id for dataset in api_response])
    return api_response

def list_tables(client, params):
    api_response = client.list_tables(params["dataset_id"])
    api_response = str([table.table_id for table in api_response])
    return api_response

def get_table(client, params):
    api_response = client.get_table(params["table_id"])
    api_response = api_response.to_api_repr()
    api_response = str(api_response)
    return api_response

def sql_query(client, params):
    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=100000000
    )  # Data limit per query job
    try:
        cleaned_query = (
            params["query"]
            .replace("\\n", " ")
            .replace("\n", "")
            .replace("\\", "")
        )
        query_job = client.query(
            cleaned_query, job_config=job_config
        )
        api_response = query_job.result()
        api_response = str([dict(row) for row in api_response])
        api_response = api_response.replace("\\", "").replace(
            "\n", ""
        )
        return api_response
    except Exception as e:
        error_message = f"""
        We're having trouble running this SQL query. This
        could be due to an invalid query or the structure of
        the data. Try rephrasing your question to help the
        model generate a valid query. Details:

        {str(e)}"""
        st.error(error_message)
        api_response = error_message
        
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )
        return api_response
    

function_handler = {
    "list_datasets": list_datasets,
    "list_tables": list_tables,
    "get_table": get_table,
    "sql_query": sql_query,
}