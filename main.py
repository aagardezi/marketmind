import time
import os
import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
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

import helperfinhub
import helpercode
import helperstreamlit


st.set_page_config(layout="wide")
# st.set_page_config()
float_init(theme=True, include_unstable_primary=False)

stringoutputcount = 0

@st.dialog("Choose the Model")
def select_model():
    logging.warning("Selecting Model")
    modelname = st.selectbox(
        "Select the Gemini version you would like to use",
        ("gemini-1.5-pro-002", "gemini-1.5-flash-002", "gemini-2.0-flash-exp"),
        index=0,
        placeholder="Select a Model",
    )
    if st.button("Choose Model"):
        logging.warning("Button pressed")
        st.session_state.modelname = modelname
        st.rerun()

def handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
    logging.warning("Starting parallal function resonse loop")
    parts=[]
    for response in response.candidates[0].content.parts:
        logging.warning("Function loop starting")
        logging.warning(response)
        params = {}
        try:
            for key, value in response.function_call.args.items():
                params[key] = value
        except AttributeError:
            continue
                
        logging.warning("Prams processing done")
        logging.warning(response)
        logging.warning(response.function_call.name)
        logging.warning(params)

        function_name = response.function_call.name

        if function_name in helperbqfunction.function_handler.keys():
            api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
            api_requests_and_responses.append(
                            [function_name, params, api_response]
                    )

        if function_name in helperfinhub.function_handler.keys():
            api_response = helperfinhub.function_handler[function_name](params)
            api_requests_and_responses.append(
                            [function_name, params, api_response]
                    )

        logging.warning("Function Response complete")

        logging.warning(api_response)

        parts.append(Part.from_function_response(
                    name=function_name,
                    response={
                        "content": api_response,
                    },
                    ),
                )

        backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

    logging.warning("Making gemin call for api response")

    # response = st.session_state.chat.send_message(
    #             parts
    #         )

    response = handle_gemini15_chat(parts)

            
    logging.warning("gemini api response completed")
    return response,backend_details


def handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
    response = response.candidates[0].content.parts[0]

    logging.warning(response)
    logging.warning("First Resonse done")

    function_calling_in_process = True
    while function_calling_in_process:
        try:
            logging.warning("Function loop starting")
            params = {}
            for key, value in response.function_call.args.items():
                params[key] = value
                    
            logging.warning("Prams processing done")
            logging.warning(response)
            logging.warning(response.function_call.name)
            logging.warning(params)

            function_name = response.function_call.name

            if function_name in helperbqfunction.function_handler.keys():
                logging.warning("BQ function found")
                api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
                api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

            if function_name in helperfinhub.function_handler.keys():
                logging.warning("finhub function found")
                api_response = helperfinhub.function_handler[function_name](params)
                api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

            logging.warning("Function Response complete")

            logging.warning(api_response)
            logging.warning("Making gemin call for api response")

            # response = st.session_state.chat.send_message(
            #             Part.from_function_response(
            #                 name=function_name,
            #                 response={
            #                     "content": api_response,
            #                 },
            #             ),
            # )
            
            part = Part.from_function_response(
                            name=function_name,
                            response={
                                "content": api_response,
                            },
            )
            response = handle_gemini15_chat_single(part)



            logging.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logging.warning("gemini api response completed")
            logging.warning(response)
            logging.warning("next call ready")
            logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
            if len(response.candidates[0].content.parts) >1:
                response, backend_details = handel_gemini15_parallel_func(handle_api_response,
                                                                        response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details)
            else:
                response = response.candidates[0].content.parts[0]


        except AttributeError as e:
            logging.warning(e)
            function_calling_in_process = False
    return response,backend_details

def handel_gemini20_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent):
    logging.warning("Starting parallal function resonse loop")
    global stringoutputcount
    parts=[]
    function_parts = []
    for response in response.candidates[0].content.parts:
        logging.warning("Function loop starting")
        logging.warning(response)
        params = {}
        try:
            for key, value in response.function_call.args.items():
                params[key] = value
        except AttributeError:
            continue
                
        logging.warning("Prams processing done")
        logging.warning(response)
        logging.warning(response.function_call.name)
        logging.warning(params)

        function_name = response.function_call.name

        if function_name in helperbqfunction.function_handler.keys():
            api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
            api_requests_and_responses.append(
                            [function_name, params, api_response]
                    )

        if function_name in helperfinhub.function_handler.keys():
            api_response = helperfinhub.function_handler[function_name](params)
            api_requests_and_responses.append(
                            [function_name, params, api_response]
                    )

        logging.warning("Function Response complete")
        stringoutputcount = stringoutputcount + len(str(api_response))
        logging.warning(f"""String output count is {stringoutputcount}""")
        logging.warning(api_response)
        function_parts.append(response)
        parts.append(types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": api_response,
                    },
                    ),
                )

        backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

    logging.warning("Making gemin call for api response")

    # response = st.session_state.chat.send_message(
    #             parts
    #         )

    response, functioncontent = handle_gemini20_chat(parts, function_parts, functioncontent)

    logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
    if len(response.candidates[0].content.parts) >1:
        response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
                                                                response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details, functioncontent)

            
    logging.warning("gemini api response completed")
    return response,backend_details, functioncontent

def handle_gemini20_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent):
    response = response.candidates[0].content.parts[0]
    global stringoutputcount
    logging.warning(response)
    logging.warning("First Resonse done")

    function_calling_in_process = True
    while function_calling_in_process:
        try:
            logging.warning("Function loop starting")
            params = {}
            for key, value in response.function_call.args.items():
                params[key] = value
                    
            logging.warning("Prams processing done")
            logging.warning(response)
            logging.warning(response.function_call.name)
            logging.warning(params)

            function_name = response.function_call.name

            if function_name in helperbqfunction.function_handler.keys():
                logging.warning("BQ function found")
                api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
                api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

            if function_name in helperfinhub.function_handler.keys():
                logging.warning("finhub function found")
                api_response = helperfinhub.function_handler[function_name](params)
                api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

            logging.warning("Function Response complete")
            stringoutputcount = stringoutputcount + len(str(api_response))
            logging.warning(f"""String output count is {stringoutputcount}""")
            logging.warning(api_response)
            logging.warning("Making gemin call for api response")

            # response = st.session_state.chat.send_message(
            #             Part.from_function_response(
            #                 name=function_name,
            #                 response={
            #                     "content": api_response,
            #                 },
            #             ),
            # )
            
            part = types.Part.from_function_response(
                            name=function_name,
                            response={
                                "result": api_response,
                            },
            )
            response, functioncontent = handle_gemini20_chat_single(part, response, functioncontent)



            logging.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logging.warning("gemini api response completed")
            logging.warning(response)
            logging.warning("next call ready")
            logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
            if len(response.candidates[0].content.parts) >1:
                response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
                                                                        response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details, functioncontent)
            else:
                response = response.candidates[0].content.parts[0]


        except AttributeError as e:
            logging.warning(e)
            function_calling_in_process = False
    return response,backend_details, functioncontent

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini15_chat(parts):
    logging.warning("Making actual multi gemini call")
    response = st.session_state.chat.send_message(
                parts
    )
    logging.warning("Multi call succeeded")
    return response

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini15_chat_single(part):
    logging.warning("Making actual single gemini call")
    response = st.session_state.chat.send_message(
                part
    )
    logging.warning("Single call succeeded")
    return response

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini20_chat(parts, function_parts, functioncontent):
    logging.warning("Making actual multi gemini call")
    # st.session_state.aicontent.append(function_parts)
    # st.session_state.aicontent.append(parts)
    functioncontent.append(function_parts)
    functioncontent.append(parts)
    try:
        response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                            #   contents=st.session_state.aicontent,
                                                              contents=functioncontent,
                                                              config=generate_config_20)
    except Exception as e:
        logging.error(e)
        raise e
    logging.warning("Multi call succeeded")
    logging.warning(response)
    logging.warning("sending response back")
    return response, functioncontent

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini20_chat_single(part, response, functioncontent):
    logging.warning("Making actual single gemini call")
    # st.session_state.aicontent.append(response)
    # st.session_state.aicontent.append(part)
    functioncontent.append(response)
    functioncontent.append(part)
    try:
        response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                            #   contents=st.session_state.aicontent,
                                                              contents=functioncontent,
                                                              config=generate_config_20)
    except Exception as e:
        logging.error(e)
        raise e
    logging.warning("Single call succeeded")
    return response, functioncontent



BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = helpercode.get_project_id()
LOCATION = "us-central1"

sql_query_tool = Tool(
    function_declarations=[
        geminifunctionsbq.sql_query_func,
        geminifunctionsbq.list_datasets_func,
        geminifunctionsbq.list_tables_func,
        geminifunctionsbq.get_table_func,
        geminifunctionsbq.sql_query_func,
        # geminifunctiongetnews.get_company_overview,
        # # get_stock_price,
        # geminifunctiongetnews.get_company_news,
        # geminifunctiongetnews.get_news_with_sentiment,
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

sql_query20_tool = types.Tool(
    function_declarations=[
        # geminifunctionsbq.sql_query_func,
        # geminifunctionsbq.list_datasets_func,
        # geminifunctionsbq.list_tables_func,
        # geminifunctionsbq.get_table_func,
        # geminifunctionsbq.sql_query_func,
        # geminifunctiongetnews.get_company_overview,
        # # get_stock_price,
        # geminifunctiongetnews.get_company_news,
        # geminifunctiongetnews.get_news_with_sentiment,
        gemini20functionfinhub.symbol_lookup,
        gemini20functionfinhub.company_news,
        gemini20functionfinhub.company_profile,
        gemini20functionfinhub.company_basic_financials,
        gemini20functionfinhub.company_peers,
        gemini20functionfinhub.insider_sentiment,
        gemini20functionfinhub.financials_reported,
        gemini20functionfinhub.sec_filings,
    ],
)

TEMP_INSTRUCTION = f"""lseg tick history data and uses RIC and ticker symbols to analyse stocks
                        When writing SQL query ensure you use the Date_Time field in the where clause.
                        {PROJECT_ID}.{BIGQUERY_DATASET_ID}.lse_normalised table is the main trade table
                        RIC is the column to search for a stock
                        When accessing news use the symbol for the company instead of the RIC cod."""

SYSTEM_INSTRUCTION = f"""You are a financial analyst that understands financial data. Do the analysis like and asset management 
                            investor and create a detaild report
                            You can lookup the symbol using the symbol lookup function. Make sure to run the symbol_lookup 
                            before any subsequent functions.
                            When doing an analysis of the company, include the company profile, company news, 
                            company basic financials and an analysis of the peers
                            Also get the insider sentiment and add a section on that. Include a section on SEC filings. If a tool 
                            requires a data and its not present the use the current year"""

PROMPT_ENHANCEMENT = """ If the question relates to news use the stock symbol ticker and not the RIC code. If a tool 
                            requires a data and its not present the use the current year. Always evalulate if the Function Call is
                            required to answer and perform function calling using the tools provided."""

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
    tools= [sql_query20_tool],
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

def handle_gemini20():
    logging.warning("Starting Gemini 2.0")
    global stringoutputcount

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if "chat" not in st.session_state:
        st.session_state.chat = client
    
    if "aicontent" not in st.session_state:
        st.session_state.aicontent = []
    
    stringoutputcount = 0

    if prompt := st.chat_input("What is up?"):

        # # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)


        # Add user message to chat history
        logging.warning(f"""Prompt is: {prompt}""")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""


            logging.warning("Configuring prompt")
            st.session_state.aicontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))
            functioncontent = []
            functioncontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))
            logging.warning("Conversation history start")
            logging.warning(st.session_state.aicontent)
            logging.warning("Conversation history end")
            logging.warning("Prompt configured, calling Gemini...")
            response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                              contents=st.session_state.aicontent,
                                                              config=generate_config_20)

            logging.warning("Gemini called, This is the start")
            logging.warning(response)
            logging.warning("The start is done")

            logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

            api_requests_and_responses = []
            backend_details = ""

            if len(response.candidates[0].content.parts) >1:
                response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent)


            else:
                response, backend_details, functioncontent = handle_gemini20_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent)

            time.sleep(3)
            
            full_response = response.text
            st.session_state.aicontent.append(types.Content(role='model', parts=[types.Part(text=full_response)]))
            with message_placeholder.container():
                st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
                with st.expander("Function calls, parameters, and responses:"):
                    st.markdown(backend_details)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "backend_details": backend_details,
                }
            )
            logging.warning(f"""Total string output count is {stringoutputcount}""")
            logging.warning(st.session_state.aicontent)
            logging.warning("This is the end of Gemini 2.0")









def handle_gemini15():
    logging.warning("Starting Gemini 1.5")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(
        # "gemini-1.5-pro-002",
        st.session_state.modelname,
        system_instruction=[SYSTEM_INSTRUCTION],
        tools=[sql_query_tool],
    )


    response=None


    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat()

    if "client" not in st.session_state:
        st.session_state.client = bigquery.Client(project="genaillentsearch")

    # with st.container():
    if prompt := st.chat_input("What is up?"):

        # # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)


        # Add user message to chat history

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response = st.session_state.chat.send_message(prompt + PROMPT_ENHANCEMENT,generation_config=generation_config,
            safety_settings=safety_settings)
            logging.warning("This is the start")
            logging.warning(response)
            logging.warning("The start is done")

            logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

            api_requests_and_responses = []
            backend_details = ""
            api_response = ""
            if len(response.candidates[0].content.parts) >1:
                response, backend_details = handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)


            else:
                response, backend_details = handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)

            time.sleep(3)

            full_response = response.text
            with message_placeholder.container():
                st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
                with st.expander("Function calls, parameters, and responses:"):
                    st.markdown(backend_details)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "backend_details": backend_details,
                }
            )





USE_AUTHENTICATION = os.getenv('USEAUTH', True)==True

logging.warning(f"""Auth as bool is set to {USE_AUTHENTICATION}""")
logging.warning(f"""Auth as string is set to {os.getenv('USEAUTH')}""")

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

logging.warning(f"""Connected status is {st.session_state['connected']} and use auth is {USE_AUTHENTICATION}""")

clientinfo = helperstreamlit.get_remote_ip()
logging.warning(f"""Client info is {clientinfo}""")


authstatus = ((not st.session_state['connected']) and ( USE_AUTHENTICATION))

logging.warning(f"""final auth status is {authstatus}""")

if authstatus:
    logging.warning("Auth Starting")
    time.sleep(5)
    authenticator.check_authentification()
    st.logo("images/mmlogo1.png")
    # Create the login button
    authenticator.login()

if st.session_state['connected'] or not USE_AUTHENTICATION:
    # st.write(f"Hello, {st.session_state['user_info'].get('name')}")
    with st.sidebar:
        st.logo("images/mmlogo1.png")
        if USE_AUTHENTICATION:
            st.image(st.session_state['user_info'].get('picture'))
            if st.button('Log out'):
                authenticator.logout()
        st.text("MarketMind")

    if "modelname" not in st.session_state:
        logging.warning("model name session state not initialised")
        # st.session_state.modelname = "gemini-1.5-pro-002"
        select_model()
        # logging.warning(f"""In initialiser function model name is {st.session_state.modelname}""")
    else:
        logging.warning(f"""model name session state initialised and it is: {st.session_state.modelname}""")
        st.image("images/mmlogo1.png")
        if USE_AUTHENTICATION:
            st.title(f"""{st.session_state['user_info'].get('name')}! MarketMind: built using {st.session_state.modelname}""")
        else:
            st.title(f"""MarketMind: built using {st.session_state.modelname}""")
        if st.session_state.modelname.startswith("gemini-1.5"):
            handle_gemini15()
        else:
            handle_gemini20()
                