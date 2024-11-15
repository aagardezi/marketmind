import streamlit as st
st.write("Hello world")

st.title("Sample AI App")

st.text("This is a sample app.")

count = 0

increment = st.button('Increment')
if increment:
    count += 1

st.write('Count = ', count)