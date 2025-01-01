import time
import traceback
import os
import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
from streamlit_pills import pills
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, Part, FinishReason, SafetySetting
from google import genai
from google.genai import types
from google.cloud import bigquery

import logging

from tenacity import retry, wait_random_exponential

import helperbqfunction
import geminifunctionsbq
import geminifunctionfinhub
import gemini20functionfinhub
import gemini20functiongeneral
import gemini20functionalphavantage

import helperfinhub
import helperalphavantage
import helpercode
import helperstreamlit

import evaluationagent
import gemini20handler
import gemini15handler

from google.cloud import pubsub_v1



BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = helpercode.get_project_id()
LOCATION = "us-central1"
USE_AUTHENTICATION = os.getenv('USEAUTH', True)==True
TOPIC_ID = os.getenv('TOPICID', "marketmind-async-topic")



#logging initialised
helpercode.init_logging()
logger = logging.getLogger("MarketMind")


stringoutputcount = 0

@st.dialog("Choose the Model")
def select_model():
    logger.warning("Selecting Model")
    modelname = st.selectbox(
        "Select the Gemini version you would like to use",
        ("gemini-1.5-pro-002", "gemini-1.5-flash-002", "gemini-2.0-flash-exp"),
        index=2,
        placeholder="Select a Model",
    )
    if st.button("Choose Model"):
        logger.warning(f"""Button pressed, model selected: {modelname}""")
        st.session_state.modelname = modelname
        st.rerun()

@st.dialog("View System Instructions", width="large")
def view_systeminstruction():
    logger.warning("Viewing System Instruction")
    st.markdown(SYSTEM_INSTRUCTION.replace('\t', ''))


def on_async_change():
    logger.warning("Async change detected")
    init_chat_session(st.session_state.gemini20, st.session_state.gemini15)
    logger.warning(f"Async status: {st.session_state.asyncagent}")
    if st.session_state.asyncagent:
        logger.warning("Setting up the publisher")
        logger.warning(f"Topic ID: {TOPIC_ID}")
        st.session_state.publisher = pubsub_v1.PublisherClient()
        st.session_state.topic_path = st.session_state.publisher.topic_path(PROJECT_ID, TOPIC_ID)

# def handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
#     logger.warning("Starting parallal function resonse loop")
#     parts=[]
#     for response in response.candidates[0].content.parts:
#         logger.warning("Function loop starting")
#         logger.warning(response)
#         params = {}
#         try:
#             for key, value in response.function_call.args.items():
#                 params[key] = value
#         except AttributeError:
#             continue
                
#         logger.warning("Prams processing done")
#         logger.warning(response)
#         logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
#         # logger.warning(params)

#         function_name = response.function_call.name

#         api_response = handle_external_function(api_requests_and_responses, params, function_name)

#         logger.warning("Function Response complete")

#         logger.warning(api_response)

#         parts.append(Part.from_function_response(
#                     name=function_name,
#                     response={
#                         "content": api_response,
#                     },
#                     ),
#                 )

#         backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

#     logger.warning("Making gemini call for api response")

#     response = handle_gemini15_chat(parts)

            
#     logger.warning("gemini api response completed")
#     return response,backend_details


# def handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
#     response = response.candidates[0].content.parts[0]

#     logger.warning(response)
#     logger.warning("First Resonse done")

#     function_calling_in_process = True
#     while function_calling_in_process:
#         try:
#             logger.warning("Function loop starting")
#             params = {}
#             for key, value in response.function_call.args.items():
#                 params[key] = value
                    
#             logger.warning("Prams processing done")
#             logger.warning(response)
#             logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
#             # logger.warning(params)

#             function_name = response.function_call.name

#             api_response = handle_external_function(api_requests_and_responses, params, function_name)

#             logger.warning("Function Response complete")

#             logger.warning(api_response)
#             logger.warning("Making gemini call for api response")
            
#             part = Part.from_function_response(
#                             name=function_name,
#                             response={
#                                 "content": api_response,
#                             },
#             )
#             response = handle_gemini15_chat_single(part)



#             logger.warning("Function Response complete")


#             backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
#             logger.warning("gemini api response completed")
#             logger.warning(response)
#             logger.warning("next call ready")
#             logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
#             if len(response.candidates[0].content.parts) >1:
#                 response, backend_details = handel_gemini15_parallel_func(handle_api_response,
#                                                                         response,
#                                                                         message_placeholder,
#                                                                         api_requests_and_responses,
#                                                                         backend_details)
#             else:
#                 response = response.candidates[0].content.parts[0]


#         except AttributeError as e:
#             logger.warning(e)
#             function_calling_in_process = False
#     return response,backend_details

# def handel_gemini20_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent):
#     logger.warning("Starting parallal function resonse loop")
#     global stringoutputcount
#     parts=[]
#     function_parts = []
#     for response in response.candidates[0].content.parts:
#         logger.warning("Function loop starting")
#         logger.warning(response)
#         params = {}
#         try:
#             for key, value in response.function_call.args.items():
#                 params[key] = value
#         except AttributeError:
#             continue
                
#         logger.warning("Prams processing done")
#         logger.warning(response)
#         logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
#         # logger.warning(params)

#         function_name = response.function_call.name

#         api_response = handle_external_function(api_requests_and_responses, params, function_name)

#         logger.warning("Function Response complete")
#         stringoutputcount = stringoutputcount + len(str(api_response))
#         logger.warning(f"""String output count is {stringoutputcount}""")
#         logger.warning(api_response)
#         function_parts.append(response)
#         parts.append(types.Part.from_function_response(
#                     name=function_name,
#                     response={
#                         "result": api_response,
#                     },
#                     ),
#                 )

#         backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

#     logger.warning("Making gemini call for api response")

#     functioncontent.append(function_parts)
#     functioncontent.append(parts)
#     response = handle_gemini20_chat(functioncontent)

#     logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
#     #testing
#     st.session_state.aicontent.append(response.candidates[0].content)
#     #testing

#     if len(response.candidates[0].content.parts) >1:
#         response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
#                                                                 response,
#                                                                         message_placeholder,
#                                                                         api_requests_and_responses,
#                                                                         backend_details, functioncontent)

            
#     logger.warning("gemini api response completed")
#     return response,backend_details, functioncontent

# def handle_gemini20_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent):
#     response = response.candidates[0].content.parts[0]
#     global stringoutputcount
#     logger.warning(response)
#     logger.warning("First Resonse done")

#     function_calling_in_process = True
#     while function_calling_in_process:
#         try:
#             logger.warning("Function loop starting")
#             params = {}
#             for key, value in response.function_call.args.items():
#                 params[key] = value
                    
#             logger.warning("Prams processing done")
#             logger.warning(response)
#             logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
#             # logger.warning(params)

#             function_name = response.function_call.name

#             api_response = handle_external_function(api_requests_and_responses, params, function_name)

#             logger.warning("Function Response complete")
#             stringoutputcount = stringoutputcount + len(str(api_response))
#             logger.warning(f"""String output count is {stringoutputcount}""")
#             logger.warning(api_response)
#             logger.warning("Making gemini call for api response")
            
#             part = types.Part.from_function_response(
#                             name=function_name,
#                             response={
#                                 "result": api_response,
#                             },
#             )

#             functioncontent.append(response)
#             functioncontent.append(part)
#             response = handle_gemini20_chat_single(functioncontent)



#             logger.warning("Function Response complete")


#             backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
#             logger.warning("gemini api response completed")
#             logger.warning(response)
#             logger.warning("next call ready")
#             logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
#             #testing
#             st.session_state.aicontent.append(response.candidates[0].content)
#             #testing

#             if len(response.candidates[0].content.parts) >1:
#                 response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
#                                                                         response,
#                                                                         message_placeholder,
#                                                                         api_requests_and_responses,
#                                                                         backend_details, functioncontent)
#             else:
#                 response = response.candidates[0].content.parts[0]


#         except AttributeError as e:
#             logger.warning(e)
#             function_calling_in_process = False
#     return response,backend_details, functioncontent


def handle_external_function(api_requests_and_responses, params, function_name):
    """This function handesl the call to the external function once Gemini has determined a function call is required"""
    if function_name in helpercode.function_handler.keys():
        logger.warning("General function found")
        api_response = helpercode.function_handler[function_name]()
        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

    if function_name in helperbqfunction.function_handler.keys():
        logger.warning("BQ function found")
        api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

    if function_name in helperfinhub.function_handler.keys():
        logger.warning("finhub function found")
        api_response = helperfinhub.function_handler[function_name](params)
        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )
    
    if function_name in helperalphavantage.function_handler.keys():
        logger.warning("alpha vantage function found")
        api_response = helperalphavantage.function_handler[function_name](params)
        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )
                
    return api_response

# @retry(wait=wait_random_exponential(multiplier=1, max=60))
# def handle_gemini15_chat(parts):
#     logger.warning("Making actual multi gemini call")
#     response = st.session_state.chat15.send_message(
#                 parts
#     )
#     logger.warning("Multi call succeeded")
#     logger.warning(response)
#     logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
#     try:
#         logger.warning("Adding messages to session state")
#         full_response = response.text
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": full_response,
#             "md5has" : helpercode.get_md5_hash(full_response)
#         })
#     except Exception as e:
#         logger.error(e)
#     logger.warning("sending response back")
#     return response

# @retry(wait=wait_random_exponential(multiplier=1, max=60))
# def handle_gemini15_chat_single(part):
#     logger.warning("Making actual single gemini call")
#     response = st.session_state.chat15.send_message(
#                 part
#     )
#     logger.warning("Single call succeeded")
#     logger.warning(response)
#     logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
#     try:
#         logger.warning("Adding messages to session state")
#         full_response = response.text
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": full_response,
#             "md5has" : helpercode.get_md5_hash(full_response)
#         })
#     except Exception as e:
#         logger.error(e)
#     logger.warning("sending response back")
#     return response

# @retry(wait=wait_random_exponential(multiplier=1, max=60))
# def handle_gemini20_chat(functioncontent):
#     logger.warning("Making actual multi gemini call")
#     # st.session_state.aicontent.append(function_parts)
#     # st.session_state.aicontent.append(parts)
#     # functioncontent.append(function_parts)
#     # functioncontent.append(parts)
#     try:
#         response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
#                                                             #   contents=st.session_state.aicontent,
#                                                               contents=functioncontent,
#                                                               config=generate_config_20)
#     except Exception as e:
#         logger.error(e)
#         raise e
#     logger.warning("Multi call succeeded")
#     logger.warning(response)
#     logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
#     try:
#         logger.warning("Adding messages to session state")
#         full_response = response.text
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": full_response,
#             "md5has" : helpercode.get_md5_hash(full_response)
#         })
#     except Exception as e:
#         logger.error(e)
#     logger.warning("sending response back")
#     return response

# @retry(wait=wait_random_exponential(multiplier=1, max=60))
# def handle_gemini20_chat_single(functioncontent):
#     logger.warning("Making actual single gemini call")
#     # st.session_state.aicontent.append(response)
#     # st.session_state.aicontent.append(part)
#     # functioncontent.append(response)
#     # functioncontent.append(part)
#     try:
#         response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
#                                                             #   contents=st.session_state.aicontent,
#                                                               contents=functioncontent,
#                                                               config=generate_config_20)
#     except Exception as e:
#         logger.error(e)
#         raise e
#     logger.warning("Single call succeeded")
#     logger.warning(response)
#     logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
#     try:
#         logger.warning("Adding messages to session state")
#         full_response = response.text
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": full_response,
#             "md5has" : helpercode.get_md5_hash(full_response)
#         })
#     except Exception as e:
#         logger.error(e)
#     logger.warning("sending response back")
#     return response

def display_restore_messages(logger):
    logger.warning("Checking if messages to restore")
    md5cache = []
    for message in st.session_state.messages:
        logger.warning("Restoring messages")
        if message["role"] in ["assistant"]:
            if(message["md5has"] not in md5cache):
                md5cache.append(message["md5has"])
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            else:
                logger.warning("Message already restored, ignoring")
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    logger.warning("Messages restored")

market_query_tool = Tool(
    function_declarations=[
        geminifunctionsbq.sql_query_func,
        geminifunctionsbq.list_datasets_func,
        geminifunctionsbq.list_tables_func,
        geminifunctionsbq.get_table_func,
        geminifunctionsbq.sql_query_func,
        geminifunctionfinhub.symbol_lookup,
        geminifunctionfinhub.company_news,
        geminifunctionfinhub.company_profile,
        geminifunctionfinhub.company_basic_financials,
        geminifunctionfinhub.company_peers,
        geminifunctionfinhub.insider_sentiment,
        geminifunctionfinhub.financials_reported,
        geminifunctionfinhub.sec_filings,
    ],
)

market_query20_tool = types.Tool(
    function_declarations=[
        # geminifunctionsbq.sql_query_func,
        # geminifunctionsbq.list_datasets_func,
        # geminifunctionsbq.list_tables_func,
        # geminifunctionsbq.get_table_func,
        # geminifunctionsbq.sql_query_func,
        gemini20functionfinhub.symbol_lookup,
        gemini20functionfinhub.company_news,
        gemini20functionfinhub.company_profile,
        gemini20functionfinhub.company_basic_financials,
        gemini20functionfinhub.company_peers,
        gemini20functionfinhub.insider_sentiment,
        gemini20functionfinhub.financials_reported,
        gemini20functionfinhub.sec_filings,
        gemini20functiongeneral.current_date,
        # gemini20functionalphavantage.monthly_stock_price,
        # gemini20functionalphavantage.market_sentiment,
    ],
)

TEMP_INSTRUCTION = f"""lseg tick history data and uses RIC and ticker symbols to analyse stocks
                        When writing SQL query ensure you use the Date_Time field in the where clause.
                        {PROJECT_ID}.{BIGQUERY_DATASET_ID}.lse_normalised table is the main trade table
                        RIC is the column to search for a stock
                        When accessing news use the symbol for the company instead of the RIC cod.
                        If a function call reqires a date range and one is not supplied always use the current year.
                        In order to get the right date use the current_date function."""

# SYSTEM_INSTRUCTION = """You are a financial analyst that understands financial data. Do the analysis like and asset management 
#                             investor and create a detaild report
#                             You can lookup the symbol using the symbol lookup function. Make sure to run the symbol_lookup 
#                             before any subsequent functions.
#                             When doing an analysis of the company, include the company profile, company news, 
#                             company basic financials and an analysis of the peers
#                             Also get the insider sentiment and add a section on that. Include a section on SEC filings. If a tool 
#                             requires a data and its not present the use the current year
#                             If a function call reqires a date range and one is not supplied always use the current year.
#                             In order to get the right date use the current_date function.
#                             Once you have the current date, use it to determine the start and end date for the year.
#                             Use those as the start and end dates in fuction calls where the user has not supplied a date range.
#                             When identifing a symbol for a company from a list of symbols make sure its a primary symbol.
#                             Usually primary symbols dont have a dot . in the name"""

SYSTEM_INSTRUCTION = """You are a highly skilled financial analyst specializing in asset management. Your task is to conduct thorough financial analysis and generate detailed reports from an investor's perspective. Follow these guidelines meticulously:

                        **1. Symbol Identification and Lookup:**

                        *   **Primary Symbol Focus:** When multiple symbols exist for a company, prioritize the *primary* symbol, which typically does *not* contain a dot (".") in its name (e.g., "AAPL" instead of "AAPL.MX").
                        *   **Mandatory Symbol Lookup:** Before executing any other functions, always use the `symbol_lookup` function to identify and confirm the correct primary symbol for the company under analysis. Do not proceed without a successful lookup.
                        *   **Handle Lookup Failures:** If `symbol_lookup` fails to identify a symbol, inform the user and gracefully end the analysis.

                        **2. Date Handling:**

                        *   **Current Date Determination:** Use the `current_date` function to obtain the current date at the beginning of each analysis. This date is critical for subsequent time-sensitive operations.
                        *   **Default Year Range:** If a function call requires a date range and the user has not supplied one, calculate the start and end dates for the *current year* using the date obtained from `current_date`. Use these as the default start and end dates in the relevant function calls.

                        **3. Analysis Components:**

                        *   **Comprehensive Report:** Your report should be comprehensive and contain the following sections:
                            *   **Company Profile:**  Include a detailed overview of the company, its industry, and its business model.
                            *   **Company News:** Summarize the latest significant news impacting the company.
                            *   **Basic Financials:** Present key financial metrics and ratios for the company, covering recent periods (using current year as default period).
                            *   **Peer Analysis:** Identify and analyze the company's key competitors, comparing their financials and market performance (current year default).
                            *   **Insider Sentiment:**  Report on insider trading activity and overall sentiment expressed by company insiders.
                            *   **SEC Filings:**  Provide an overview of the company's recent SEC filings, highlighting any significant disclosures (current year as default).

                        **4. Data Handling and Error Management:**

                        *   **Data Completeness:** If a function requires date that is not present or unavailable, use the current year as the default period. Report missing data but don't let it stop you.
                        *   **Function Execution:** Execute functions carefully, ensuring you have the necessary data, especially dates and symbols, before invoking any function.
                        *   **Clear Output:** Present results in a clear and concise manner, suitable for an asset management investor.

                        **5. Analytical Perspective:**

                        *   **Asset Management Lens:** Conduct all analysis with an asset manager's perspective in mind. Evaluate the company as a potential investment, focusing on risk, return, and long-term prospects.

                        **Example Workflow (Implicit):**

                        1.  Get the current date using `current_date`.
                        2.  Use `symbol_lookup` to identify the primary symbol for the company provided by the user.
                        3.  If no symbol is found, end the process and report back.
                        4.  Calculate the start and end date for the current year based on the date from step 1.
                        5.  Call the relevant functions to retrieve the company profile, news, financials, peers, insider sentiment, and SEC filings. Use the current year start and end date when required, or the date specified by the user.
                        6.  Assemble a detailed and insightful report that addresses each of the sections mentioned above.
                        """

TEMP_SYSTEM_INSTRUCTION = """
                            When creating the report also inlcude a seciton on market sentiment (accessed via a tool) and 
                            use the monthly stock prices (obtained via a tool) and review it as part of the analysis"""

PROMPT_ENHANCEMENT = """ If the question relates to news use the stock symbol ticker and not the RIC code. If a tool 
                            requires a data and its not present the use the current year. Always evalulate if the Function Call is
                            required to answer and perform function calling using the tools provided. 
                            If a function call reqires a date range and one is not supplied always use the current year.
                            In order to get the right date use the current_date function.
                            Always include a disclaimer at the end showing this report has been generated by AI and thus 
                            does not constitute financial advice"""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

generate_config_20 = types.GenerateContentConfig(
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
    tools= [market_query20_tool],
)

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]


def handle_api_response(message_placeholder, api_requests_and_responses, backend_details):
    backend_details += "- Function call:\n"
    backend_details += (
                        "   - Function name: ```"
                        + str(api_requests_and_responses[-1][0])
                        + "```"
                    )
    backend_details += "\n\n"
    backend_details += (
                        "   - Function parameters: ```"
                        + str(api_requests_and_responses[-1][1])
                        + "```"
                    )
    backend_details += "\n\n"
    backend_details += (
                        "   - API response: ```"
                        + str(api_requests_and_responses[-1][2])
                        + "```"
                    )
    backend_details += "\n\n"
    with message_placeholder.container():
        st.markdown(backend_details)
    return backend_details

# def handle_gemini20(prompt):
#     logger.warning("Starting Gemini 2.0")
#     global stringoutputcount

#     # client = genai.Client(
#     #     vertexai=True,
#     #     project=PROJECT_ID,
#     #     location=LOCATION
#     # )

#     # if "chat" not in st.session_state:
#     #     st.session_state.chat = client
    
#     # if "aicontent" not in st.session_state:
#     #     st.session_state.aicontent = []
    
#     stringoutputcount = 0

#     # if prompt := st.chat_input("What is up?"):

#     #     # # Display user message in chat message container
#     #     with st.chat_message("user"):
#     #         st.markdown(prompt)


#     # Add user message to chat history
#     logger.warning(f"""Model is: {st.session_state.modelname}, Prompt is: {prompt}""")


#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""


#         logger.warning("Configuring prompt")
#         st.session_state.aicontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))
#         functioncontent = []
#         functioncontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))

#         evaluationagent.evaluation_agent(prompt)

#         logger.warning("Conversation history start")
#         logger.warning(st.session_state.aicontent)
#         logger.warning("Conversation history end")
#         logger.warning("Prompt configured, calling Gemini...")
#         response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
#                                                             contents=st.session_state.aicontent,
#                                                             config=generate_config_20)

#         logger.warning("Gemini called, This is the start")
#         logger.warning(response)
#         logger.warning(f"""Tokens in use: {response.usage_metadata}""")
#         logger.warning("The start is done")

#         logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

#         api_requests_and_responses = []
#         backend_details = ""
#         #testing
#         st.session_state.aicontent.append(response.candidates[0].content)
#         #testing
#         if len(response.candidates[0].content.parts) >1:
#             response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent)


#         else:
#             response, backend_details, functioncontent = handle_gemini20_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent)

#         time.sleep(3)
        
#         full_response = response.text
#         # st.session_state.aicontent.append(types.Content(role='model', parts=[types.Part(text=full_response)]))
#         with message_placeholder.container():
#             st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
#             with st.expander("Function calls, parameters, and responses:"):
#                 st.markdown(backend_details)

#         st.session_state.messages.append(
#             {
#                 "role": "assistant",
#                 "content": full_response,
#                 "backend_details": backend_details,
#                 "md5has" : helpercode.get_md5_hash(full_response)
#             }
#         )
#         logger.warning(f"""Total string output count is {stringoutputcount}""")
#         logger.warning(st.session_state.aicontent)
#         logger.warning("This is the end of Gemini 2.0")


# def handle_gemini15(prompt):
#     logger.warning("Starting Gemini 1.5")
#     vertexai.init(project=PROJECT_ID, location=LOCATION)
#     # model = GenerativeModel(
#     #     # "gemini-1.5-pro-002",
#     #     st.session_state.modelname,
#     #     system_instruction=[SYSTEM_INSTRUCTION],
#     #     tools=[market_query_tool],
#     # )


#     response=None


#     # if "chat15" not in st.session_state:
#     #     st.session_state.chat15 = model.start_chat()

#     # if prompt := st.chat_input("What is up?"):

#     #     # # Display user message in chat message container
#     #     with st.chat_message("user"):
#     #         st.markdown(prompt)


#     # Add user message to chat history

#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""
        
#         response = st.session_state.chat15.send_message(prompt + PROMPT_ENHANCEMENT,generation_config=generation_config,
#         safety_settings=safety_settings)
#         logger.warning("This is the start")
#         logger.warning(response)
#         logger.warning(f"""Tokens in use: {response.usage_metadata}""")
#         logger.warning("The start is done")

#         logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

#         api_requests_and_responses = []
#         backend_details = ""
#         api_response = ""
#         if len(response.candidates[0].content.parts) >1:
#             response, backend_details = handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)


#         else:
#             response, backend_details = handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)

#         time.sleep(3)

#         full_response = response.text
#         with message_placeholder.container():
#             st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
#             with st.expander("Function calls, parameters, and responses:"):
#                 st.markdown(backend_details)

#         st.session_state.messages.append(
#             {
#                 "role": "assistant",
#                 "content": full_response,
#                 "backend_details": backend_details,
#                 "md5has" : helpercode.get_md5_hash(full_response)
#             }
#         )





def authenticate_user(logger, PROJECT_ID, USE_AUTHENTICATION):
    logger.warning(f"""Auth as bool is set to {USE_AUTHENTICATION}""")
    logger.warning(f"""Auth as string is set to {os.getenv('USEAUTH')}""")

    authenticator = Authenticate(
        secret_credentials_path=helpercode.create_temp_credentials_file(helpercode.access_secret_version(PROJECT_ID, "AssetMPlatformKey")),
        cookie_name='logincookie',
        cookie_key='this_is_secret',
        redirect_uri='https://marketmind-884152252139.us-central1.run.app/',
    )

    # if not st.session_state.get('connected', False):
    #     authorization_url = authenticator.get_authorization_url()
    #     st.markdown(f'[Login]({authorization_url})')
    #     st.link_button('Login', authorization_url)

    logger.warning(f"""Connected status is {st.session_state['connected']} and use auth is {USE_AUTHENTICATION}""")

    clientinfo = helperstreamlit.get_remote_ip()
    logger.warning(f"""Client info is {clientinfo}""")


    authstatus = ((not st.session_state['connected']) and ( USE_AUTHENTICATION))


    logger.warning(f"""final auth status is {authstatus}""")

    if authstatus:
        logger.warning("Auth Starting")
        time.sleep(5)
        authenticator.check_authentification()
        st.logo("images/mmlogo1.png")
    # Create the login button
        authenticator.login()
    return authenticator


def get_chat_history():
    messages = []
    messageicon = []
    for message in st.session_state.messages:
        if message["role"] in ["user"]:
            messages.append(message['content'][:15])
            messageicon.append('➕')
    if len(messages) > 0:
        with st.sidebar:
            pills("Chat History", messages, messageicon)

def init_chat_session(client, model):
    st.session_state.messages = []
    st.session_state.sessioncount = 0
    st.session_state.client = bigquery.Client(project="genaillentsearch")
    st.session_state.chat = client
    st.session_state.aicontent = []
    st.session_state.chat15 = model.start_chat()


def display_sidebar(logger, view_systeminstruction, USE_AUTHENTICATION, get_chat_history, init_chat_session, authenticator):
    with st.sidebar:
        st.logo("images/mmlogo1.png")
        if USE_AUTHENTICATION:
            st.image(st.session_state['user_info'].get('picture'))
            if st.button('Log out'):
                authenticator.logout()
        st.header("MarketMind")
        st.toggle("Async Agent",False, on_change=on_async_change, key="asyncagent")
        get_chat_history()
        if st.button("Start new Chat"):
            init_chat_session(st.session_state.gemini20, st.session_state.gemini15)
            st.rerun()
        st.header("Debug")
        if st.button("Reload"):
            pass
        if st.button("System Instruction"):
            view_systeminstruction()
            
        st.session_state.sessioncount = st.session_state.sessioncount +1
        logger.warning(f"""Session count is {st.session_state.sessioncount}""")
        st.text(f"""#: {st.session_state.sessioncount}""")
        st.text(f"AsyncAgent: {st.session_state.asyncagent}")

def send_async_gemini_message(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    future = st.session_state.publisher.publish(st.session_state.topic_path,
                                        prompt.encode("utf-8"),
                                        model = st.session_state.modelname.encode("utf-8"),
                                        session_id = st.session_state.session_id)
                
    logger.warning(f"Published message, status: {future.result()}")


st.set_page_config(layout="wide")
# st.set_page_config()
float_init(theme=True, include_unstable_primary=False)

authenticator = authenticate_user(logger, PROJECT_ID, USE_AUTHENTICATION)

if st.session_state['connected'] or not USE_AUTHENTICATION:

    if "modelname" not in st.session_state:
        logger.warning("model name session state not initialised")
        # st.session_state.modelname = "gemini-1.5-pro-002"
        select_model()
        # logger.warning(f"""In initialiser function model name is {st.session_state.modelname}""")
    else:
        logger.warning(f"""model name session state initialised and it is: {st.session_state.modelname}""")
        if "chatstarted" not in st.session_state:
            #Gemini 2 client
            client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location=LOCATION
            )

            #Gemini1.5 Client
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            model = GenerativeModel(
                # "gemini-1.5-pro-002",
                st.session_state.modelname,
                system_instruction=[SYSTEM_INSTRUCTION],
                tools=[market_query_tool],
            )
            st.session_state.gemini15 = model
            st.session_state.gemini20 = client
            init_chat_session(client, model)
            st.session_state.chatstarted = True
            if "session_id" not in st.session_state:
                st.session_state.session_id = str(uuid.uuid4())
            

        # if "messages" not in st.session_state:
        #     st.session_state.messages = []
        # st.write(f"Hello, {st.session_state['user_info'].get('name')}")
        display_sidebar(logger, view_systeminstruction, USE_AUTHENTICATION, get_chat_history, init_chat_session, authenticator)

        # if "modelname" not in st.session_state:
        #     logger.warning("model name session state not initialised")
        #     # st.session_state.modelname = "gemini-1.5-pro-002"
        #     select_model()
        #     # logger.warning(f"""In initialiser function model name is {st.session_state.modelname}""")
        # else:
        
        st.image("images/mmlogo1.png")
        if USE_AUTHENTICATION:
            st.title(f"""{st.session_state['user_info'].get('name')}! MarketMind: built using {st.session_state.modelname}""")
        else:
            st.title(f"""MarketMind: built using {st.session_state.modelname}""")
        
        st.caption("Currently only available for US Securities")

        # if "sessioncount" not in st.session_state:
        #     st.session_state.sessioncount = 0
        # else:
        # st.session_state.sessioncount = st.session_state.sessioncount +1
        
        # logger.warning(f"""Session count is {st.session_state.sessioncount}""")

        # with st.sidebar:
        #     st.text(f"""#: {st.session_state.sessioncount}""")

        # st.text(f"""Currently only available for US Securities {st.session_state.sessioncount}""")

        display_restore_messages(logger)
        
        # if "client" not in st.session_state:
        #     st.session_state.client = bigquery.Client(project="genaillentsearch")
        try:
            if prompt := st.chat_input("What is up?"):
                # # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(prompt)
                if st.session_state.asyncagent:
                    send_async_gemini_message(prompt)
                    with st.chat_message("assistant"):
                        st.markdown("Message sent awaiting response...")
                else:
                    if st.session_state.modelname.startswith("gemini-1.5"):
                        gemini15handler.handle_gemini15(prompt, logger, PROJECT_ID, LOCATION, PROMPT_ENHANCEMENT, 
                                                        generation_config, safety_settings, handle_api_response, handle_external_function)
                    else:
                        gemini20handler.handle_gemini20(prompt, logger, PROJECT_ID, LOCATION, PROMPT_ENHANCEMENT, 
                                                        generate_config_20, handle_api_response, handle_external_function)
        except Exception as e:
            with st.chat_message("error",avatar=":material/chat_error:"):
                message_placeholder = st.empty()
                with message_placeholder.container():
                    with st.expander("Error message and stack trace"):
                        st.markdown(f"An error occurred: {e}")
                        st.markdown(traceback.format_exc())
                