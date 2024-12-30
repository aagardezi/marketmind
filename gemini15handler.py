import time

import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
from streamlit_pills import pills
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, Part, FinishReason, SafetySetting



from tenacity import retry, wait_random_exponential

import helpercode



def handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, logger, handle_external_function):
    logger.warning("Starting parallal function resonse loop")
    parts=[]
    for response in response.candidates[0].content.parts:
        logger.warning("Function loop starting")
        logger.warning(response)
        params = {}
        try:
            for key, value in response.function_call.args.items():
                params[key] = value
        except AttributeError:
            continue
                
        logger.warning("Prams processing done")
        logger.warning(response)
        logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
        # logger.warning(params)

        function_name = response.function_call.name

        api_response = handle_external_function(api_requests_and_responses, params, function_name)

        logger.warning("Function Response complete")

        logger.warning(api_response)

        parts.append(Part.from_function_response(
                    name=function_name,
                    response={
                        "content": api_response,
                    },
                    ),
                )

        backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

    logger.warning("Making gemini call for api response")

    response = handle_gemini15_chat(parts)

            
    logger.warning("gemini api response completed")
    return response,backend_details


def handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, logger, handle_external_function):
    response = response.candidates[0].content.parts[0]

    logger.warning(response)
    logger.warning("First Resonse done")

    function_calling_in_process = True
    while function_calling_in_process:
        try:
            logger.warning("Function loop starting")
            params = {}
            for key, value in response.function_call.args.items():
                params[key] = value
                    
            logger.warning("Prams processing done")
            logger.warning(response)
            logger.warning(f"""FunctionName: {response.function_call.name} Params: {params}""")
            # logger.warning(params)

            function_name = response.function_call.name

            api_response = handle_external_function(api_requests_and_responses, params, function_name)

            logger.warning("Function Response complete")

            logger.warning(api_response)
            logger.warning("Making gemini call for api response")
            
            part = Part.from_function_response(
                            name=function_name,
                            response={
                                "content": api_response,
                            },
            )
            response = handle_gemini15_chat_single(part)



            logger.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logger.warning("gemini api response completed")
            logger.warning(response)
            logger.warning("next call ready")
            logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
            if len(response.candidates[0].content.parts) >1:
                response, backend_details = handel_gemini15_parallel_func(handle_api_response,
                                                                        response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details,
                                                                        logger, handle_external_function)
            else:
                response = response.candidates[0].content.parts[0]


        except AttributeError as e:
            logger.warning(e)
            function_calling_in_process = False
    return response,backend_details

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini15_chat(parts, logger):
    logger.warning("Making actual multi gemini call")
    response = st.session_state.chat15.send_message(
                parts
    )
    logger.warning("Multi call succeeded")
    logger.warning(response)
    logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
    try:
        logger.warning("Adding messages to session state")
        full_response = response.text
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "md5has" : helpercode.get_md5_hash(full_response)
        })
    except Exception as e:
        logger.error(e)
    logger.warning("sending response back")
    return response

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini15_chat_single(part, logger):
    logger.warning("Making actual single gemini call")
    response = st.session_state.chat15.send_message(
                part
    )
    logger.warning("Single call succeeded")
    logger.warning(response)
    logger.warning(f"""Tokens in use: {response.usage_metadata}""")
    
    try:
        logger.warning("Adding messages to session state")
        full_response = response.text
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "md5has" : helpercode.get_md5_hash(full_response)
        })
    except Exception as e:
        logger.error(e)
    logger.warning("sending response back")
    return response


def handle_gemini15(prompt, logger, PROJECT_ID, LOCATION, PROMPT_ENHANCEMENT, generation_config, safety_settings, handle_api_response, handle_external_function):
    logger.warning("Starting Gemini 1.5")
    # vertexai.init(project=PROJECT_ID, location=LOCATION)
    # model = GenerativeModel(
    #     # "gemini-1.5-pro-002",
    #     st.session_state.modelname,
    #     system_instruction=[SYSTEM_INSTRUCTION],
    #     tools=[market_query_tool],
    # )


    response=None


    # if "chat15" not in st.session_state:
    #     st.session_state.chat15 = model.start_chat()

    # if prompt := st.chat_input("What is up?"):

    #     # # Display user message in chat message container
    #     with st.chat_message("user"):
    #         st.markdown(prompt)


    # Add user message to chat history

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = st.session_state.chat15.send_message(prompt + PROMPT_ENHANCEMENT,generation_config=generation_config,
        safety_settings=safety_settings)
        logger.warning("This is the start")
        logger.warning(response)
        logger.warning(f"""Tokens in use: {response.usage_metadata}""")
        logger.warning("The start is done")

        logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

        api_requests_and_responses = []
        backend_details = ""
        api_response = ""
        if len(response.candidates[0].content.parts) >1:
            response, backend_details = handel_gemini15_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, logger, handle_external_function)


        else:
            response, backend_details = handle_gemini15_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, logger, handle_external_function)

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
                "md5has" : helpercode.get_md5_hash(full_response)
            }
        )
