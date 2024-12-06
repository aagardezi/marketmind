import time
import tempfile
import json
import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, Part, FinishReason, SafetySetting
from google.cloud import bigquery
from google.cloud import secretmanager
import google.auth
import logging

import helpergetnews
import helperbqfunction
import geminifunctionsbq

import geminifunctionfinhub
import geminifunctiongetnews
import helperfinhub


st.set_page_config(layout="wide")
float_init(theme=True, include_unstable_primary=False)

c1, c2 = st.columns((1, 3))

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


def get_project_id():
  """Gets the current GCP project ID.

  Returns:
    The project ID as a string.
  """

  try:
    _, project_id = google.auth.default()
    return project_id
  except google.auth.exceptions.DefaultCredentialsError as e:
    print(f"Error: Could not determine the project ID. {e}")
    return None

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

    response = st.session_state.chat.send_message(
                parts
            )
            
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

            response = st.session_state.chat.send_message(
                        Part.from_function_response(
                            name=function_name,
                            response={
                                "content": api_response,
                            },
                        ),
                    )

            logging.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logging.warning("gemini api response completed")
            logging.warning(response)
            logging.warning("next call ready")
            response = response.candidates[0].content.parts[0]


        except AttributeError:
            logging.warning(Exception)
            function_calling_in_process = False
    return response,backend_details



BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = get_project_id()

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

# st.write("Hello world")

# st.text("This is a sample app.")

# def increment_counter():
#     st.session_state.count += 2

# if 'count' not in st.session_state:
#     st.session_state.count = 0

# if "celsius" not in st.session_state:
#     # set the initial default value of the slider widget
#     st.session_state.celsius = 50.0

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


def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    logging.warning(response.payload.data.decode("UTF-8"))
    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")

def create_temp_credentials_file(credentials_json):
    """
    Writes a JSON object to a temporary file and returns the file path.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix='.json') as temp_file:
        temp_file.write(credentials_json)
    temp_file_path = temp_file.name
    logging.warning(temp_file_path)
    
    with open(temp_file_path, 'r', encoding='utf-8') as f:  # Opens the file in read mode with UTF-8 encoding
        contents = f.read()
        logging.warning(contents)

    return temp_file_path




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

authenticator = Authenticate(
    secret_credentials_path=create_temp_credentials_file(access_secret_version(PROJECT_ID, "AssetMPlatformKey")),
    cookie_name='logincookie',
    cookie_key='this_is_secret',
    redirect_uri='https://marketmind-884152252139.us-central1.run.app/',
)

# if not st.session_state.get('connected', False):
#     authorization_url = authenticator.get_authorization_url()
#     st.markdown(f'[Login]({authorization_url})')
#     st.link_button('Login', authorization_url)


if not st.session_state['connected']:
    time.sleep(5)
    authenticator.check_authentification()

# Create the login button
    authenticator.login()

if st.session_state['connected']:
    # st.write(f"Hello, {st.session_state['user_info'].get('name')}")
    with c1:
        st.image(st.session_state['user_info'].get('picture'))
        if st.button('Log out'):
            authenticator.logout()
    with c2:
        if "modelname" not in st.session_state:
            logging.warning("model name session state not initialised")
            st.session_state.modelname = "gemini-1.5-pro-002"
            select_model()
            logging.warning(f"""In initialiser function model name is {st.session_state.modelname}""")
        else:
            logging.warning("model name session state initialised")

            st.title(f"""Hello: {st.session_state['user_info'].get('name')}! MarketMind: built using {st.session_state.modelname}""")
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
                                    Also get the insider sentiment and add a section on that. Include a section on SEC filings."""],
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

            with st.container():
                if prompt := st.chat_input("What is up?"):
                    # button_b_pos = "0rem"
                    # button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
                    # float_parent(css=button_css)
                    # # Display user message in chat message container
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    prompt_enhancement = """ If the question requires SQL data then Make sure you get the data from the sql query first and then analyse it in its completeness if not get the news directly
                            If the question relates to news use the stock symbol ticker and not the RIC code."""

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


                        # if len(response.candidates[0].content.parts) >1:
                        #     logging.warning("Starting parallal function resonse loop")
                        #     parts=[]
                        #     for response in response.candidates[0].content.parts:
                        #         logging.warning("Function loop starting")
                        #         logging.warning(response)
                        #         params = {}
                        #         try:
                        #             for key, value in response.function_call.args.items():
                        #                 params[key] = value
                        #         except AttributeError:
                        #             continue
                                
                        #         logging.warning("Prams processing done")
                        #         logging.warning(response)
                        #         logging.warning(response.function_call.name)
                        #         logging.warning(params)

                        #         function_name = response.function_call.name

                        #         if function_name in helperbqfunction.function_handler.keys():
                        #             api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
                        #             api_requests_and_responses.append(
                        #                     [function_name, params, api_response]
                        #             )

                        #         if function_name in helperfinhub.function_handler.keys():
                        #             api_response = helperfinhub.function_handler[function_name](params)
                        #             api_requests_and_responses.append(
                        #                     [function_name, params, api_response]
                        #             )

                        #         logging.warning("Function Response complete")

                        #         logging.warning(api_response)

                        #         parts.append(Part.from_function_response(
                        #             name=function_name,
                        #             response={
                        #                 "content": api_response,
                        #             },
                        #             ),
                        #         )

                        #         backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

                        #     logging.warning("Making gemin call for api response")

                        #     response = st.session_state.chat.send_message(
                        #         parts
                        #     )
                            
                        #     logging.warning("gemini api response completed")


                        # else:
                        #     response = response.candidates[0].content.parts[0]

                        #     # api_requests_and_responses = []
                        #     # backend_details = ""
                        #     # api_response = ""


                        #     logging.warning(response)
                        #     logging.warning("First Resonse done")

                        #     function_calling_in_process = True
                        #     while function_calling_in_process:
                        #         try:
                        #             logging.warning("Function loop starting")
                        #             params = {}
                        #             for key, value in response.function_call.args.items():
                        #                 params[key] = value
                                    
                        #             logging.warning("Prams processing done")
                        #             logging.warning(response)
                        #             logging.warning(response.function_call.name)
                        #             logging.warning(params)

                        #             function_name = response.function_call.name

                        #             # if function_name in helpergetnews.function_handler.keys():
                        #             #     logging.warning("Getnews function found")
                        #             #     # Extract the function call name
                        #             #     # function_name = response.function_call.name
                        #             #     logging.warning("#### Predicted function name")
                        #             #     logging.warning(function_name, "\n")

                        #             #     # Extract the function call parameters
                        #             #     # params = {key: value for key, value in response.function_call.args.items()}
                        #             #     logging.warning("#### Predicted function parameters")
                        #             #     logging.warning(params, "\n")

                        #             #     # Invoke a function that calls an external API
                        #             #     api_response = helpergetnews.function_handler[function_name](params)
                        #             #     logging.warning("#### API response")
                        #             #     logging.warning(api_response[:500], "...", "\n")

                        #             #     api_requests_and_responses.append(
                        #             #             [function_name, params, api_response]
                        #             #     )

                        #             if function_name in helperbqfunction.function_handler.keys():
                        #                 logging.warning("BQ function found")
                        #                 api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
                        #                 api_requests_and_responses.append(
                        #                         [function_name, params, api_response]
                        #                 )

                        #             if function_name in helperfinhub.function_handler.keys():
                        #                 logging.warning("finhub function found")
                        #                 api_response = helperfinhub.function_handler[function_name](params)
                        #                 api_requests_and_responses.append(
                        #                         [function_name, params, api_response]
                        #                 )

                        #             logging.warning("Function Response complete")

                        #             logging.warning(api_response)
                        #             logging.warning("Making gemin call for api response")

                        #             response = st.session_state.chat.send_message(
                        #                 Part.from_function_response(
                        #                     name=function_name,
                        #                     response={
                        #                         "content": api_response,
                        #                     },
                        #                 ),
                        #             )

                        #             logging.warning("Function Response complete")

                        #             # backend_details += "- Function call:\n"
                        #             # backend_details += (
                        #             #     "   - Function name: ```"
                        #             #     + str(api_requests_and_responses[-1][0])
                        #             #     + "```"
                        #             # )
                        #             # backend_details += "\n\n"
                        #             # backend_details += (
                        #             #     "   - Function parameters: ```"
                        #             #     + str(api_requests_and_responses[-1][1])
                        #             #     + "```"
                        #             # )
                        #             # backend_details += "\n\n"
                        #             # backend_details += (
                        #             #     "   - API response: ```"
                        #             #     + str(api_requests_and_responses[-1][2])
                        #             #     + "```"
                        #             # )
                        #             # backend_details += "\n\n"
                        #             # with message_placeholder.container():
                        #             #     st.markdown(backend_details)

                        #             backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                                    
                        #             logging.warning("gemini api response completed")
                        #             logging.warning(response)
                        #             logging.warning("next call ready")
                        #             response = response.candidates[0].content.parts[0]


                        #         except AttributeError:
                        #             logging.warning(Exception)
                        #             function_calling_in_process = False

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

                