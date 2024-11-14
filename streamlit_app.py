import json
import streamlit as st
from openai import OpenAI

st.markdown("""
    <style>
    .stTextInput, .stTextArea {
        margin-top: -5%;  /* Set margin-top to 0 to remove space above */
    }
    </style>
""", unsafe_allow_html=True)

st.title("Community Input Categorizer")

st.write("Please enter a sentence about what you'd like to see in your neighborhood.")
user_input = st.text_input("")

openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

with open('data.json', 'r') as f:
    json_content = json.load(f)

json_content_str = json.dumps(json_content)


if user_input:
    st.write(f"You entered: *{user_input}*")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You analyze user input into JSON data. The JSON must have these fields: "
                    "category, typology, and keywords (that exist in the input). There could be multiple JSONs for keywords that belong under different categories."
                    "Use only the category and typology values present in the following JSON structure:\n"
                    f"{json_content_str}"
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
    )

    st.write(response.choices[0].message.content)