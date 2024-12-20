
import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate


from google import genai
from google.genai import types
from google.cloud import bigquery

import logging



import gemini20functionfinhub

import gemini20functionevalagent


import helpercode


SYSTEM_INSTRUCTION = """You are an AI evaluation agent an your job is to take the prompt and evaluate the list of companies
                        mentiond and use that along with the tools to identify the symbols for the company and return the 
                        function or tool calls with the right parameters in order to be able to evaluate the individual
                        companies/symbols mentioned."""

PROJECT_ID = helpercode.get_project_id()
LOCATION = "us-central1"

logger = logging.getLogger("MarketMind")

evalagent_20_tool = types.Tool(
    function_declarations=[
        # geminifunctionsbq.sql_query_func,
        # geminifunctionsbq.list_datasets_func,
        # geminifunctionsbq.list_tables_func,
        # geminifunctionsbq.get_table_func,
        # geminifunctionsbq.sql_query_func,
        gemini20functionfinhub.symbol_lookup,
        # gemini20functionfinhub.company_news,
        # gemini20functionfinhub.company_profile,
        # gemini20functionfinhub.company_basic_financials,
        # gemini20functionfinhub.company_peers,
        # gemini20functionfinhub.insider_sentiment,
        # gemini20functionfinhub.financials_reported,
        # gemini20functionfinhub.sec_filings,
        # gemini20functiongeneral.current_date,
        # gemini20functionalphavantage.monthly_stock_price,
        # gemini20functionalphavantage.market_sentiment,
        gemini20functionevalagent.company_evaluation,
    ],
)

generate_config_evalagent = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    system_instruction=[types.Part.from_text(SYSTEM_INSTRUCTION)],
    tools= [evalagent_20_tool],
)

def evaluation_agent(prompt):
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    aicontent = []
    logger.warning("Strating Eval agnet")
    aicontent.append(types.Content(role='user', parts=[types.Part(text=prompt)]))
    response = client.models.generate_content(model=st.session_state.modelname,
                                                              contents=aicontent,
                                                              config=generate_config_evalagent)
    logger.warning("Eval agent done")
    logger.warning(response)
