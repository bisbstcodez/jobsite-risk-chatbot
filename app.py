import streamlit as st
import pandas as pd
from openai import OpenAI

# Load OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load risk knowledge base
risk_data = pd.read_csv("risk_data.csv")

st.set_page_config(page_title="🏗️ Jobsite Risk Advisor", page_icon="🏗️")
st.title("🏗️ Jobsite Risk Advisor Chatbot")
st.write("Describe your site issue. I’ll evaluate the risk and suggest mitigation.")

user_input = st.text_area("Enter your site condition or issue:", height=150)

def identify_relevant_risks(text, data):
    matches = []
    for _, row in data.iterrows():
        if any(tag.strip().lower() in text.lower() for tag in row['tags'].split(',')):
            matches.append(row)
    return matches

def generate_ai_response(user_text, matched_risks):
    risks_text = ""
    for risk in matched_risks:
        risks_text += f"- **Risk Type:** {risk['risk_type']}\n"
        risks_text += f"  - Description: {risk['description']}\n"
        risks_text += f"  - Estimated Delay: {risk['impact_range_days']} days\n"
        risks_text += f"  - Recommended Action: {risk['recommended_action']}\n\n"

    if not risks_text:
        risks_text = "No direct matches found, but here's general advice:"

    prompt = f"""
You are a construction risk advisor. Interpret the user's issue and suggest risk types, delay impacts, and mitigation strategies.

User input: "{user_text}"

Relevant risks:
{risks_text}

Respond in 1–2 clear, professional paragraphs.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

if st.button("Evaluate Risk") and user_input:
    matched_risks = identify_relevant_risks(user_input, risk_data)
    ai_response = generate_ai_response(user_input, matched_risks)
    st.markdown("### 🧠 Risk Evaluation")
    st.markdown(ai_response)