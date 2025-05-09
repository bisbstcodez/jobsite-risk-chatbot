import streamlit as st
import pandas as pd
from openai import OpenAI
from PIL import Image

# Load OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load risk knowledge base
try:
    risk_data = pd.read_csv("risk_data.csv", on_bad_lines='warn', encoding='utf-8', delimiter=',')
except Exception as e:
    st.error(f"⚠️ Failed to load risk data: {e}")
    risk_data = pd.DataFrame()  # Use empty DataFrame to prevent crashes

# Page configuration
st.set_page_config(page_title="Jobsite Risk Advisor")

# Load and display custom logo above the title (stacked layout)
try:
    logo = Image.open("logo.png")
    st.image(logo, width=300)
except:
    pass  # If logo not found, continue without crashing

# App title centered under logo
st.markdown("<h1 style='text-align: center;'>Jobsite Risk Advisor</h1>", unsafe_allow_html=True)

st.write("This AI Chatbot supports Construction Managers in Risk Assessment and Mitigation for Large Construciton Project. Start by selecting an example prompt below, then type a custom prompt in the text box if necessary. I’ll evaluate the risk and recommend mitigation steps.")

# Starter prompts
example_prompts = {
    "weather": "Heavy rain has delayed concrete pouring by 2 days.",
    "permit": "We’re still waiting on the city to approve our trenching permit.",
    "safety": "A worker slipped on loose gravel near the lift station."
}

# Session state for persistent input
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Buttons to insert starter examples
st.markdown("#### 📝 Example site issues:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌧️ Weather Delay"):
        st.session_state.user_input = example_prompts["weather"]
with col2:
    if st.button("📋 Permit Issue"):
        st.session_state.user_input = example_prompts["permit"]
with col3:
    if st.button("⚠️ Safety Concern"):
        st.session_state.user_input = example_prompts["safety"]

# Reset input
if st.button("🔄 Reset Input"):
    st.session_state.user_input = ""

# Text area with persisted input
user_input = st.text_area(
    "Enter your site condition or issue:",
    value=st.session_state.user_input,
    height=150
)
st.session_state.user_input = user_input  # keep updated

# Function to match risks from CSV
def identify_relevant_risks(text, data):
    matches = []
    for _, row in data.iterrows():
        if any(tag.strip().lower() in text.lower() for tag in row['tags'].split(',')):
            matches.append(row)
    return matches

# Function to generate OpenAI response
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
        return f"⚠️ Error generating response: {e}"

# Evaluate button
if st.button("✅ Evaluate Risk") and user_input.strip():
    matched_risks = identify_relevant_risks(user_input, risk_data)
    ai_response = generate_ai_response(user_input, matched_risks)
    st.markdown("### 🧠 Risk Evaluation")
    st.markdown(ai_response)
