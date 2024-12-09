import time
import os
import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, Part, FinishReason, SafetySetting
from google.cloud import bigquery
from google.cloud import secretmanager
import logging

from tenacity import retry, wait_random_exponential

import helperbqfunction
import geminifunctionsbq

import geminifunctionfinhub

import helperfinhub

import helpercode

st.set_page_config(layout="wide")
# st.set_page_config()
float_init(theme=True, include_unstable_primary=False)


@st.dialog("Choose the Model")
def select_model():
    modelname = st.selectbox(
        "Select the Gemini version you would like to use",
        ("gemini-1.5-pro-002", "gemini-1.5-flash-002"),
        index=0,
        placeholder="Select a Model",
    )
    if st.button("Choose Model"):
        st.session_state.modelname = modelname
        st.rerun()

def handel_gemini_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
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

    response = handle_gemini_chat(parts)

            
    logging.warning("gemini api response completed")
    return response,backend_details


def handle_gemini_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details):
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
            response = handle_gemini_chat_single(part)



            logging.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logging.warning("gemini api response completed")
            logging.warning(response)
            logging.warning("next call ready")
            logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
            response = response.candidates[0].content.parts[0]


        except AttributeError:
            logging.warning(Exception)
            function_calling_in_process = False
    return response,backend_details

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini_chat(parts):
    logging.warning("Making actual multi gemini call")
    response = st.session_state.chat.send_message(
                parts
    )
    logging.warning("Multi call succeeded")
    return response

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini_chat_single(part):
    logging.warning("Making actual single gemini call")
    response = st.session_state.chat.send_message(
                part
    )
    logging.warning("Single call succeeded")
    return response



BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = helpercode.get_project_id()

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


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

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


USE_AUTHENTICATION = os.getenv('USEAUTH', True)


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


if (not st.session_state['connected']) and USE_AUTHENTICATION:
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

    if "modelname" not in st.session_state:
        logging.warning("model name session state not initialised")
        st.session_state.modelname = "gemini-1.5-pro-002"
        select_model()
        logging.warning(f"""In initialiser function model name is {st.session_state.modelname}""")
    else:
        logging.warning("model name session state initialised")
        st.image("images/mmlogo1.png")
        if USE_AUTHENTICATION:
            st.title(f"""Hello: {st.session_state['user_info'].get('name')}! MarketMind: built using {st.session_state.modelname}""")
        else:
            st.title(f"""Hello! MarketMind: built using {st.session_state.modelname}""")
        vertexai.init(project=PROJECT_ID, location="us-central1")
        model = GenerativeModel(
            # "gemini-1.5-pro-002",
            st.session_state.modelname,
            system_instruction=[f"""You are a financial analyst that understands financial data. Do the analysis like and asset management investor and create a detaild report
                                lseg tick history data and uses RIC and ticker symbols to analyse stocks
                                When writing SQL query ensure you use the Date_Time field in the where clause. {PROJECT_ID}.{BIGQUERY_DATASET_ID}.lse_normalised table is the main trade table
                                RIC is the column to search for a stock
                                When accessing news use the symbol for the company instead of the RIC cod.
                                You can lookup the symbol using the symbol lookup function. Make sure to run the symbol_lookup before any subsequent functions.
                                When doing an analysis of the company, include the company profile, company news, company basic financials and an analysis of the peers
                                Also get the insider sentiment and add a section on that. Include a section on SEC filings. If a tool 
                                requires a data and its not present the use the current year"""],
            tools=[sql_query_tool],
        )

        # st.button('Increment Even', on_click=increment_counter)

        # st.write('Count = ', st.session_state.count)

        # st.slider(
        #     "Temperature in Celsius",
        #     min_value=-100.0,
        #     max_value=100.0,
        #     key="celsius"
        # )

        # # This will get the value of the slider widget
        # st.write(st.session_state.celsius)
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
            # button_b_pos = "0rem"
            # button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            # float_parent(css=button_css)
            # # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            prompt_enhancement = """ If the question requires SQL data then Make sure you get the data from the sql query first and then analyse it in its completeness if not get the news directly
                    If the question relates to news use the stock symbol ticker and not the RIC code. If a tool 
                                requires a data and its not present the use the current year"""

            # prompt += prompt_enhancement
            # Add user message to chat history

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                response = st.session_state.chat.send_message(prompt + prompt_enhancement,generation_config=generation_config,
                safety_settings=safety_settings)
                logging.warning("This is the start")
                logging.warning(response)
                logging.warning("The start is done")

                logging.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

                api_requests_and_responses = []
                backend_details = ""
                api_response = ""
                if len(response.candidates[0].content.parts) >1:
                    response, backend_details = handel_gemini_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)


                else:
                    response, backend_details = handle_gemini_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details)

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



                # with message_placeholder.container():
                #     message_placeholder.markdown(response.text)
                # st.session_state.messages.append({"role": "assistant", "content": response.text})

                