import streamlit as st
st.write("Hello world")

st.title("Sample AI App")

st.text("This is a sample app.")

if 'count' not in st.session_state:
    st.session_state.count = 0
 

increment = st.button('Increment')
if increment:
    st.session_state.count += 1

st.write('Count = ', st.session_state.count)