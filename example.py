from text_highlighter import text_highlighter
import streamlit as st

# Basic usage
result = text_highlighter(
    text="Cats and dogs in the Netherlands are awesome!", labels=["ANIMAL", "LOCATION"]
)

# Show the results
st.write(result)
