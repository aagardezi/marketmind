import time
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, Part, FinishReason, SafetySetting
from google.cloud import bigquery
import logging

import helpergetnews
import helperbqfunction
import geminifunctionsbq

import geminifunctionfinhub
import geminifunctiongetnews
import helperfinhub


BIGQUERY_DATASET_ID = "lseg_data_normalised"
PROJECT_ID = "genaillentsearch"



@st.dialog("Choose the Model")
def select_model():
    model_name = st.selectbox(
    "Select the Gemini version you would like to use",
    ("gemini-1.5-pro-002", "gemini-1.5-flash-002"),
    index=0,
    placeholder="Select a Model",
    key="model_name"
    
    )
    if st.button("Choose Model"):
        st.session_state.model_name = model_name
        st.rerun()




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



if "model_name" not in st.session_state:
   select_model()
else:
    

    st.title(f"""Company Agent: built using {st.session_state.model_name}""")

    model = GenerativeModel(
        # "gemini-1.5-pro-002",
        st.session_state.model_name,
        system_instruction=[f"""You are a financial analysit that understands lseg tick history data and uses RIC and ticker symbols to analyse stocks
        When writing SQL query ensure you use the Date_Time field in the where clause. {PROJECT_ID}.{BIGQUERY_DATASET_ID}.lse_normalised table is the main trade table
                    RIC is the column to search for a stock
                    When accessing news use the symbol for the company instead of the RIC cod.
                    You can lookup the symbol using the symbol lookup function. Make sure to run the symbol_lookup before any subsequent functions.
                    When doing an analysis of the company, include the company profile, company news, company basic financials and an analysis of the peers"""],
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

    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
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

            response = response.candidates[0].content.parts[0]

            api_requests_and_responses = []
            backend_details = ""
            api_response = ""


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

                    if function_name in helpergetnews.function_handler.keys():
                        # Extract the function call name
                        # function_name = response.function_call.name
                        logging.warning("#### Predicted function name")
                        logging.warning(function_name, "\n")

                        # Extract the function call parameters
                        # params = {key: value for key, value in response.function_call.args.items()}
                        logging.warning("#### Predicted function parameters")
                        logging.warning(params, "\n")

                        # Invoke a function that calls an external API
                        api_response = helpergetnews.function_handler[function_name](params)
                        logging.warning("#### API response")
                        logging.warning(api_response[:500], "...", "\n")

                        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )

                        # Send the API response back to Gemini, which will generate a natural language summary or another function call
                        # response = st.session_state.chat.send_message(
                        #     Part.from_function_response(
                        #         name=function_name,
                        #         response={"content": function_api_response},
                        #     ),
                        # )

                        # backend_details += "- Function call:\n"
                        # backend_details += (
                        #     "   - Function name: ```"
                        #     + str(api_requests_and_responses[-1][0])
                        #     + "```"
                        # )
                        # backend_details += "\n\n"
                        # backend_details += (
                        #     "   - Function parameters: ```"
                        #     + str(api_requests_and_responses[-1][1])
                        #     + "```"
                        # )
                        # backend_details += "\n\n"
                        # backend_details += (
                        #     "   - API response: ```"
                        #     + str(api_requests_and_responses[-1][2])
                        #     + "```"
                        # )
                        # backend_details += "\n\n"
                        # with message_placeholder.container():
                        #     st.markdown(backend_details)

                        # response = response.candidates[0].content.parts[0]
                        # full_response = response.text
                        # with message_placeholder.container():
                        #     st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
                        #     with st.expander("Function calls, parameters, and responses:"):
                        #         st.markdown(backend_details)

                        # st.session_state.messages.append(
                        #     {
                        #         "role": "assistant",
                        #         "content": full_response,
                        #         "backend_details": backend_details,
                        #     }
                        # )
                    

                    if function_name in helperbqfunction.function_handler.keys():
                        api_response = helperbqfunction.function_handler[function_name](st.session_state.client, params)
                        api_requests_and_responses.append(
                                [function_name, params, api_response]
                        )


                    # if response.function_call.name == "list_datasets":
                    #     api_response = st.session_state.client.list_datasets()
                    #     api_response = BIGQUERY_DATASET_ID
                    #     logging.warning(api_response)
                    #     api_response = str([dataset.dataset_id for dataset in api_response])
                    #     api_requests_and_responses.append(
                    #         [response.function_call.name, params, api_response]
                    #     )

                    # if response.function_call.name == "list_tables":
                    #     api_response = st.session_state.client.list_tables(params["dataset_id"])
                    #     api_response = str([table.table_id for table in api_response])
                    #     api_requests_and_responses.append(
                    #         [response.function_call.name, params, api_response]
                    #     )

                    # if response.function_call.name == "get_table":
                    #     api_response = st.session_state.client.get_table(params["table_id"])
                    #     api_response = api_response.to_api_repr()
                    #     api_requests_and_responses.append(
                    #         [
                    #             response.function_call.name,
                    #             params,
                    #             [
                    #                 str(api_response.get("description", "")),
                    #                 str(
                    #                     [
                    #                         column["name"]
                    #                         for column in api_response["schema"][
                    #                             "fields"
                    #                         ]
                    #                     ]
                    #                 ),
                    #             ],
                    #         ]
                    #     )
                    #     api_response = str(api_response)

                    # if response.function_call.name == "sql_query":
                    #     job_config = bigquery.QueryJobConfig(
                    #         maximum_bytes_billed=100000000
                    #     )  # Data limit per query job
                    #     try:
                    #         cleaned_query = (
                    #             params["query"]
                    #             .replace("\\n", " ")
                    #             .replace("\n", "")
                    #             .replace("\\", "")
                    #         )
                    #         query_job = st.session_state.client.query(
                    #             cleaned_query, job_config=job_config
                    #         )
                    #         api_response = query_job.result()
                    #         api_response = str([dict(row) for row in api_response])
                    #         api_response = api_response.replace("\\", "").replace(
                    #             "\n", ""
                    #         )
                    #         api_requests_and_responses.append(
                    #             [response.function_call.name, params, api_response]
                    #         )
                    #     except Exception as e:
                    #         error_message = f"""
                    #         We're having trouble running this SQL query. This
                    #         could be due to an invalid query or the structure of
                    #         the data. Try rephrasing your question to help the
                    #         model generate a valid query. Details:

                    #         {str(e)}"""
                    #         st.error(error_message)
                    #         api_response = error_message
                    #         api_requests_and_responses.append(
                    #             [response.function_call.name, params, api_response]
                    #         )
                    #         st.session_state.messages.append(
                    #             {
                    #                 "role": "assistant",
                    #                 "content": error_message,
                    #             }
                    #         )

                    if function_name in helperfinhub.function_handler.keys():
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
                    response = response.candidates[0].content.parts[0]

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
                    
                    logging.warning("gemini api response completed")

                except AttributeError:
                    function_calling_in_process = False

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

        