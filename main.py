import streamlit as st
st.write("Hello world")

st.title("Sample AI App")

st.text("This is a sample app.")

def increment_counter():
    st.session_state.count += 2

if 'count' not in st.session_state:
    st.session_state.count = 0
 

st.button('Increment Even', on_click=increment_counter)

st.write('Count = ', st.session_state.count)

