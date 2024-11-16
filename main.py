import streamlit as st
from vertexai.generative_models import GenerativeModel, Part, FinishReason, SafetySetting

st.write("Hello world")

st.title("Sample AI App")

st.text("This is a sample app.")

def increment_counter():
    st.session_state.count += 2

if 'count' not in st.session_state:
    st.session_state.count = 0

if "celsius" not in st.session_state:
    # set the initial default value of the slider widget
    st.session_state.celsius = 50.0

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

model = GenerativeModel(
    "gemini-1.5-flash-002",
    #system_instruction=["""answer in pirate lingo"""]
)

st.button('Increment Even', on_click=increment_counter)

st.write('Count = ', st.session_state.count)

st.slider(
    "Temperature in Celsius",
    min_value=-100.0,
    max_value=100.0,
    key="celsius"
)

# This will get the value of the slider widget
st.write(st.session_state.celsius)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = st.session_state.chat.send_message(prompt,generation_config=generation_config,
        safety_settings=safety_settings)
        
        response = response.candidates[0].content.parts[0]
        with message_placeholder.container():
            message_placeholder.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    