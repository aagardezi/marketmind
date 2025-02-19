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
import json

from tenacity import retry, wait_random_exponential

import helperbqfunction
import geminifunctionsbq
import geminifunctionfinhub
import gemini20functionfinhub
import gemini20functiongeneral
import gemini20functionalphavantage
import gemini20functionshareprice

import helperfinhub
import helperalphavantage
import helpercode
import helperstreamlit
import helperfunctionshareprice


import gemini20handler
import gemini15handler

from google.cloud import pubsub_v1



BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = helpercode.get_project_id()
LOCATION = "us-central1"
USE_AUTHENTICATION = os.getenv('USEAUTH', True)==True
TOPIC_ID = os.getenv('TOPICID', "marketmind-async-topic")

HELP = """You can use the this to create an analyst report for US stocks and companies.
The Gemini based agent uses finhub.io to access their data API via tools and analyse the data to create the report.
Once you generate the report you can chat with the data/responses or ask to create a new report. 
The reports can also be compared and summarised. You can ask a full question or just the symbol for a company (GOOGL / META). 
For example you can ask the following
* Can you create an analyst report for the company ALPHABET INC-CL A that includes basic financials, company news for the year 2024 and
company profile . Include the actual numbers as well. Include a summary of the analysis as well.
* Can you create an analyst report for the company META
* Can you compare the above analyst reprots and give me a sumary list pros and cons with a rating (Buy, Sell, Hold)

or

* GOOGL for the last 6 months
* META for the last 6 months"""

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

@st.dialog("View help", width="large")
def view_help():
    logger.warning("Viewing Help")
    st.markdown(HELP)

def on_async_change():
    logger.warning("Async change detected")
    init_chat_session(st.session_state.gemini20, st.session_state.gemini15)
    logger.warning(f"Async status: {st.session_state.asyncagent}")
    if st.session_state.asyncagent:
        logger.warning("Setting up the publisher")
        logger.warning(f"Topic ID: {TOPIC_ID}")
        st.session_state.publisher = pubsub_v1.PublisherClient()
        st.session_state.topic_path = st.session_state.publisher.topic_path(PROJECT_ID, TOPIC_ID)



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
    
    if function_name in helperfunctionshareprice.function_handler.keys():
        logger.warning("share proce function found")
        api_response = helperfunctionshareprice.function_handler[function_name](params)
        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )
    
                
    return api_response



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
        gemini20functionshareprice.shareprice
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

                        *   **Comprehensive Report:** Your report should be comprehensive, detailed and contain the following sections:
                            *   **Company Profile:**  Include a detailed overview of the company, its industry, and its business model.
                            *   **Company News:** Summarize the latest significant news impacting the company. Make it detailed.
                            *   **Basic Financials:** Present key financial metrics and ratios for the company, covering recent periods (using current year as default period).
                            *   **Peer Analysis:** Identify and analyze the company's key competitors, comparing their financials and market performance (current year default).
                            *   **Insider Sentiment:**  Report on insider trading activity and overall sentiment expressed by company insiders.
                            *   **SEC Filings:**  Provide an overview of the company's recent SEC filings, highlighting any significant disclosures and a summary of the findings. Make it detailed.

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
                        4.  Calculate the start and end date by using the result of the current_date tool.
                        5.  Call the relevant functions to retrieve the company profile, news, financials, peers, insider sentiment, and SEC filings. Use the current year start and end date when required, or the date specified by the user.
                        6.  Assemble a detailed and insightful report that addresses each of the sections mentioned above.
                        """

TEMP_SYSTEM_INSTRUCTION = """
                            When creating the report also inlcude a seciton on market sentiment (accessed via a tool) and 
                            use the monthly stock prices (obtained via a tool) and review it as part of the analysis"""

PROMPT_ENHANCEMENT = """ If the question relates to news use the stock symbol ticker and not the RIC code. If a tool 
                            requires a data and its not present the use the current year. Always evalulate if the Function Call is
                            required to answer and perform function calling using the tools provided. 
                            If a function call reqires a date range and one is not supplied always use the last 6 months which can be 
                            calculated using the current_date function tool.
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
    system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTION)],
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

        if st.button("Help"):
            view_help()
        if st.button("Reload"):
            pass
        if st.button("System Instruction"):
            view_systeminstruction()
            
        st.session_state.sessioncount = st.session_state.sessioncount +1
        logger.warning(f"""Session count is {st.session_state.sessioncount}""")
        st.text(f"""#: {st.session_state.sessioncount}""")
        st.text(f"AsyncAgent: {st.session_state.asyncagent}")

def serialise_message(aicontent):
    returndata = []
    logger.warning("priting aicontent")
    logger.warning(aicontent)
    logger.warning("priting aicontent done")
    for item in aicontent:
        returndata.append({
            "role": item.role,
            "content": item.parts[0].text
        })
    
    testing_data = []
    for item in returndata:
        testing_data.append(types.Content(role=item["role"], parts=[types.Part(text=item["content"])]))
    
    logger.warning("priting testing_data")
    logger.warning(testing_data)
    logger.warning("priting testing_data done")

    return json.dumps(returndata).encode("utf-8")   

def send_async_gemini_message(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.aicontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))
    future = st.session_state.publisher.publish(st.session_state.topic_path,
                                        serialise_message(st.session_state.aicontent),
                                        model = st.session_state.modelname.encode("utf-8"),
                                        session_id = st.session_state.session_id,
                                        prompt = prompt.encode("utf-8"))
    st.session_state.aysncmessagesent = True
                
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
                logging.warning(f"Session id created: {st.session_state.session_id}")
            

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
        
        st.caption(f"Currently only available for US Securities -- {helpercode._get_session().id}")

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
                    send_async_gemini_message(prompt+PROMPT_ENHANCEMENT)
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
                