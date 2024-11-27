import json
import os
import streamlit as st
from openai import OpenAI
from datetime import datetime
import csv
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def update_frequency_data_by_month(user_inputs, frequency_data):
    for entry in user_inputs:
        # year and month extracted from date
        month_year = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
        
        # extract data from entry dictionary
        data = entry['data']
        
        # make sure data is dict
        if isinstance(data, dict):
            category = data['category']
            typology = data['typology']
            keywords = data['keywords']  # this is a list of keywords
            
            # check frequency data for the given month exists
            if month_year not in frequency_data:
                frequency_data[month_year] = {"categories": {}}
            
            if category not in frequency_data[month_year]["categories"]:
                frequency_data[month_year]["categories"][category] = {"typologies": {}}
            
            if typology not in frequency_data[month_year]["categories"][category]["typologies"]:
                frequency_data[month_year]["categories"][category]["typologies"][typology] = {
                    "count": 0,
                    "keywords": {}
                }
            
            # update typology counts
            frequency_data[month_year]["categories"][category]["typologies"][typology]["count"] += 1
            
            # update keyword counts
            for keyword in keywords:
                if keyword in frequency_data[month_year]["categories"][category]["typologies"][typology]["keywords"]:
                    frequency_data[month_year]["categories"][category]["typologies"][typology]["keywords"][keyword] += 1
                else:
                    frequency_data[month_year]["categories"][category]["typologies"][typology]["keywords"][keyword] = 1
        
    return frequency_data

with open('data.json', 'r') as f:
    json_content = json.load(f)

# loading user inputs data
if os.path.exists('user_inputs.json'):
    with open('user_inputs.json', 'r') as f:
        user_inputs = json.load(f)
else:
    user_inputs = []

# loading freq data
if os.path.exists('frequency_data.json'):
    with open('frequency_data.json', 'r') as f:
        frequency_data = json.load(f)
else:
    frequency_data = {}


# st.markdown("""
#     <style>
#     .stTextInput, .stTextArea {
#         margin-top: -5%;  /* Set margin-top to 0 to remove space above */
#     }
#     </style>
# """, unsafe_allow_html=True)

st.title("Welcome to CommunityDIAL")

st.write("Please enter a sentence about what you'd like to see in your neighborhood.")

with st.form('chat_input_form'):
    # Create two columns; adjust the ratio to your liking
    col1, col2 = st.columns([7,1]) 

    # Use the first column for text input
    with col1:
        user_input = st.text_input(
            "",
            label_visibility='collapsed'
        )
    # Use the second column for the submit button
    with col2:
        submitted = st.form_submit_button('Submit')


hide_input_instructions_css = """
<style>
div[data-testid="InputInstructions"] > span:nth-child(1) {
    visibility: hidden;
}
</style>
"""

st.markdown(hide_input_instructions_css, unsafe_allow_html=True)

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

    response_json = response.choices[0].message.content
    clean_response = response_json.strip("```json\n").strip("```").strip()
    clean = json.loads(clean_response)

    selected_category = clean[0]["category"]
    selected_typology = clean[0]["typology"]

    col1, col2 = st.columns([2,6])

    with col1:
        st.write(response_json)

    with col2:
        categories = json_content["categories"]
        rows = len(categories) // 5 + len(categories) % 2  # Calculate rows for a 5x2 grid

        for i in range(rows):
            row = st.columns(5)  # Create a row with five columns
            
            # Handle two categories per row
            for j in range(5):
                idx = i * 5 + j
                if idx < len(categories):
                    category_data = categories[idx]
                    category_name = category_data["name"]
                    typologies = category_data["typologies"]

                    # Highlight logic
                    if category_name == selected_category:
                        category_style = f"<span style='background-color: blue; color: white; padding: 5px;'>{category_name}</span>"
                        typologies_style = "\n".join(
                        [f"<span style='color: blue; font-weight: bold;'>{t}</span>" if t == selected_typology else f"<span style='color: gray;'>{t}</span>"
                        for t in typologies]
                        )
                    else:
                        category_style = f"<span style='color:gray;'>{category_name}</span>"
                        typologies_style = "\n".join([f"<span style='color:gray;'>{t}</span>" for t in typologies])

                    # Render in the grid
                    with row[j]:
                        st.markdown(f"<h5>{category_style}</h5>", unsafe_allow_html=True)
                        st.markdown(f"<p>{typologies_style}</p>", unsafe_allow_html=True)

# col1, col2 = st.columns([2,9])

# with col1:
#     st.write("hello")

# with col2:
#     row1 = st.columns(5)
#     row2 = st.columns(5)

#     for col in row1 + row2:
#         tile = col.container(border=True)
#         tile.subheader("Category")
#         multi = '''ndfnkf
#         nfdjncsdncjf
#         '''
#         tile.markdown(multi)

    

    # st.write(f"Cleaned API response: {clean_response}")

    response_with_date = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": json.loads(clean_response)
    }

    user_inputs.append(response_with_date)

    with open('user_inputs.json', 'w') as f:
        json.dump(user_inputs, f, indent=4)
    
    frequency_data = update_frequency_data_by_month(user_inputs, frequency_data)

    with open('frequency_data.json', 'w') as f:
        json.dump(frequency_data, f, indent=4)
    

# def update_monthly_csv(frequency_data, filename='monthly_frequency_data.csv'):
#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         # header
#         writer.writerow(['Date', 'Commercial', 'Recreation', 'Cultural', 'Civic', 'Housing', 'Health', 'Entertainment', 'Transport', 'Education', 'Agriculture'])
#         for date, date_data in frequency_data.items():
#             monthly_counts = defaultdict(int)
#             for category, category_data in date_data['categories'].items():
#                 total_count = sum(typology_data['count'] for typology_data in category_data['typologies'].values())
#                 monthly_counts[category] = total_count
#             writer.writerow([date, monthly_counts['Commercial'], monthly_counts['Recreation'], monthly_counts['Cultural'], monthly_counts['Civic']])

# update_monthly_csv(frequency_data)

# def load_csv(filename='monthly_frequency_data.csv'):
#     return pd.read_csv(filename)

# df = load_csv()

# data_rows = []
# for date, date_info in frequency_data.items():
#     for category, category_info in date_info["categories"].items():
#         total_count = 0
#         for typology, typology_info in category_info.get("typologies", {}).items():
#             count = typology_info.get("count", 0)
#             total_count += count
#         # Append row for the category
#         data_rows.append({"date": date, "category": category, "count": total_count})

# # Create DataFrame
# df = pd.DataFrame(data_rows)

# df.to_csv("category_trends.csv", index=False)

# st.area_chart(df, x="date", y="count", color="category", stack="center")

# categories = ['Commercial', 'Recreation', 'Cultural', 'Civic', 'Housing', 'Health', 'Entertainment', 'Transport', 'Education', 'Agriculture']
# dates = df['Date'].tolist()

# data = {
#     category: df[category].tolist() for category in categories
# }

# fig = go.Figure()

# for category, counts in data.items():
#     fig.add_trace(go.Scatter(
#         x=dates, 
#         y=counts, 
#         mode='lines',
#         stackgroup='one',  # This groups the lines into a single stack
#         name=category
#     ))

# fig.update_layout(
#     title='communityDIAL',
#     xaxis_title='Date',
#     yaxis_title='Count',
#     template='plotly_dark',  
#     xaxis=dict(
#         tickmode='array',
#         tickvals=dates,
#         tickangle=45  
#     ),
#     yaxis=dict(
#         rangemode="tozero" 
#     ),
#     showlegend=True
# )

# st.plotly_chart(fig)
