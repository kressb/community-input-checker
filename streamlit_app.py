import json
import os
import streamlit as st
from openai import OpenAI

with open('data.json', 'r') as f:
    json_content = json.load(f)

# Initialize or load user inputs
if os.path.exists('user_inputs.json'):
    with open('user_inputs.json', 'r') as f:
        user_inputs = json.load(f)
else:
    user_inputs = []

# Initialize or load frequency data
if os.path.exists('frequency_data.json'):
    with open('frequency_data.json', 'r') as f:
        frequency_data = json.load(f)
else:
    frequency_data = {}



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

    # st.write(response.choices[0].message.content)
    response_json = json.loads(response.choices[0].message.content)
    st.write(response_json)

    user_inputs.append(response_json)
    with open('user_inputs.json', 'w') as f:
        json.dump(user_inputs, f, indent=4)