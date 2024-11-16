import streamlit as st
from vertexai.generative_models import GenerativeModel, Part, FinishReason

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


model = GenerativeModel(
    "gemini-1.5-flash-002"
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

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat = model.start_chat()
        response = chat.send_message(prompt)
        response = response.candidates[0].content.parts[0]
        with message_placeholder.container():
            message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    
