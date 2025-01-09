import time

import streamlit as st
from streamlit_float import *
from streamlit_google_auth import Authenticate
from streamlit_pills import pills

from google import genai
from google.genai import types


from tenacity import retry, wait_random_exponential

import helpercode


import evaluationagent



def handel_gemini20_parallel_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent, handle_external_function, generate_config_20, logger):
    logger.warning("Starting parallal function resonse loop")
    global stringoutputcount
    parts=[]
    function_parts = []
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
        stringoutputcount = stringoutputcount + len(str(api_response))
        logger.warning(f"""String output count is {stringoutputcount}""")
        logger.warning(api_response)
        function_parts.append(response)
        parts.append(types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": api_response,
                    },
                    ),
                )

        backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)

    logger.warning("Making gemini call for api response")

    functioncontent.append(function_parts)
    functioncontent.append(parts)
    response = handle_gemini20_chat(functioncontent, logger, generate_config_20)

    logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
    #testing
    st.session_state.aicontent.append(response.candidates[0].content)
    #testing

    if len(response.candidates[0].content.parts) >1:
        response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
                                                                response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details, functioncontent,
                                                                        handle_external_function, generate_config_20, logger)

            
    logger.warning("gemini api response completed")
    return response,backend_details, functioncontent

def handle_gemini20_serial_func(handle_api_response, response, message_placeholder, api_requests_and_responses, backend_details, functioncontent, handle_external_function, generate_config_20, logger):
    response = response.candidates[0].content.parts[0]
    global stringoutputcount
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
            stringoutputcount = stringoutputcount + len(str(api_response))
            logger.warning(f"""String output count is {stringoutputcount}""")
            logger.warning(api_response)
            logger.warning("Making gemini call for api response")
            
            part = types.Part.from_function_response(
                            name=function_name,
                            response={
                                "result": api_response,
                            },
            )

            functioncontent.append(response)
            functioncontent.append(part)
            response = handle_gemini20_chat_single(functioncontent, logger, generate_config_20)



            logger.warning("Function Response complete")


            backend_details = handle_api_response(message_placeholder, api_requests_and_responses, backend_details)
                    
            logger.warning("gemini api response completed")
            logger.warning(response)
            logger.warning("next call ready")
            logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")
            #testing
            st.session_state.aicontent.append(response.candidates[0].content)
            #testing

            if len(response.candidates[0].content.parts) >1:
                response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response,
                                                                        response,
                                                                        message_placeholder,
                                                                        api_requests_and_responses,
                                                                        backend_details, functioncontent, handle_external_function, 
                                                                        generate_config_20, logger)
            else:
                response = response.candidates[0].content.parts[0]


        except AttributeError as e:
            logger.warning(e)
            function_calling_in_process = False
    return response,backend_details, functioncontent


@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handle_gemini20_chat(functioncontent, logger, generate_config_20):
    logger.warning("Making actual multi gemini call")
    # st.session_state.aicontent.append(function_parts)
    # st.session_state.aicontent.append(parts)
    # functioncontent.append(function_parts)
    # functioncontent.append(parts)
    try:
        response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                            #   contents=st.session_state.aicontent,
                                                              contents=functioncontent,
                                                              config=generate_config_20)
    except Exception as e:
        logger.error(e)
        raise e
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
def handle_gemini20_chat_single(functioncontent, logger, generate_config_20):
    logger.warning("Making actual single gemini call")
    # st.session_state.aicontent.append(response)
    # st.session_state.aicontent.append(part)
    # functioncontent.append(response)
    # functioncontent.append(part)
    try:
        response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                            #   contents=st.session_state.aicontent,
                                                              contents=functioncontent,
                                                              config=generate_config_20)
    except Exception as e:
        logger.error(e)
        raise e
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

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def handel_initial_gemini20_chat(generate_config_20, logger):
    try:
        response = st.session_state.chat.models.generate_content(model=st.session_state.modelname,
                                                            contents=st.session_state.aicontent,
                                                            config=generate_config_20)
    except Exception as e:
        logger.error(e)
        raise e                                                    
    return response

def handle_gemini20(prompt, logger, PROJECT_ID, LOCATION, PROMPT_ENHANCEMENT, generate_config_20, handle_api_response, handle_external_function):
    logger.warning("Starting Gemini 2.0")
    global stringoutputcount

    # client = genai.Client(
    #     vertexai=True,
    #     project=PROJECT_ID,
    #     location=LOCATION
    # )

    # if "chat" not in st.session_state:
    #     st.session_state.chat = client
    
    # if "aicontent" not in st.session_state:
    #     st.session_state.aicontent = []
    
    stringoutputcount = 0

    # if prompt := st.chat_input("What is up?"):

    #     # # Display user message in chat message container
    #     with st.chat_message("user"):
    #         st.markdown(prompt)


    # Add user message to chat history
    logger.warning(f"""Model is: {st.session_state.modelname}, Prompt is: {prompt}""")


    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""


        logger.warning("Configuring prompt")
        st.session_state.aicontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))
        functioncontent = []
        functioncontent.append(types.Content(role='user', parts=[types.Part(text=prompt+PROMPT_ENHANCEMENT )]))

        # evaluationagent.evaluation_agent(prompt)

        logger.warning("Conversation history start")
        logger.warning(st.session_state.aicontent)
        logger.warning("Conversation history end")
        logger.warning("Prompt configured, calling Gemini...")
        response = handel_initial_gemini20_chat(generate_config_20, logger)

        logger.warning("Gemini called, This is the start")
        logger.warning(response)
        logger.warning(f"""Tokens in use: {response.usage_metadata}""")
        logger.warning("The start is done")

        logger.warning(f"""Length of functions is {len(response.candidates[0].content.parts)}""")

        api_requests_and_responses = []
        backend_details = ""
        #testing
        st.session_state.aicontent.append(response.candidates[0].content)
        #testing
        if len(response.candidates[0].content.parts) >1:
            response, backend_details, functioncontent = handel_gemini20_parallel_func(handle_api_response, response, 
                                                                                       message_placeholder, api_requests_and_responses, 
                                                                                       backend_details, functioncontent, 
                                                                                       handle_external_function, generate_config_20,
                                                                                       logger)


        else:
            response, backend_details, functioncontent = handle_gemini20_serial_func(handle_api_response, response, 
                                                                                     message_placeholder, api_requests_and_responses, 
                                                                                     backend_details, functioncontent, 
                                                                                     handle_external_function, generate_config_20, 
                                                                                     logger)

        time.sleep(3)
        
        full_response = response.text
        # st.session_state.aicontent.append(types.Content(role='model', parts=[types.Part(text=full_response)]))
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
        logger.warning(f"""Total string output count is {stringoutputcount}""")
        logger.warning(st.session_state.aicontent)
        logger.warning("This is the end of Gemini 2.0")
