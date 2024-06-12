from text_highlighter import text_highlighter
import streamlit as st

# Basic usage
result = text_highlighter(
    text="John Doe is the founder of MyComp Inc. and lives in New York with his wife Jane Doe. The company was "
    "founded in 2010 and has since grown to 100 employees.",
    labels=[("PERSON", "red"), ("ORG", "#0000FF")],
    # Optionally you can specify pre-existing annotations:
    annotations=[
        {"start": 0, "end": 8, "tag": "PERSON"},
        {"start": 27, "end": 38, "tag": "ORG"},
        {"start": 75, "end": 83, "tag": "PERSON"},
    ],
)

# Show the results (in XML format)
st.code(result.to_xml())

# Show the results (as a list)
st.write(result)
