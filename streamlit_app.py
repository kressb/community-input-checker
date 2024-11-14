import json
import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Community Input Checker")
st.write(
    "Please enter a sentence about what you'd like to see in your neighborhood."
)

openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

with open('data.json', 'r') as f:
    json_content = json.load(f)

json_content_str = json.dumps(json_content)

user_input = st.text_input("Input here:")

if user_input:
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