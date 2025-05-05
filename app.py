import streamlit as st
import pandas as pd
from openai import OpenAI
from PIL import Image

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load risk knowledge base
risk_data = pd.read_csv("risk_data.csv")

# Page configuration
st.set_page_config(page_title="🏗️ Jobsite Risk Advisor", page_icon="🏗️")

# Optional: Load logo if available
try:
    logo = Image.open("logo.png")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo, width=80)
    with col2:
        st.title("🏗️ Jobsite Risk Advisor")
except:
    st.title("🏗️ Jobsite Risk Advisor")

st.write("Describe your site issue below. I’ll evaluate the risk and recommend mitigation steps.")

# Example starter prompts
example_prompts = {
    "weather": "Heavy rain has delayed concrete pouring by 2 days.",
    "permit": "We’re still waiting on the city to approve our trenching permit.",
    "safety": "A worker slipped on loose gravel near the lift station."
}

# Initialize session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Display text area
user_input = st.text_area(
    "Enter your site condition or issue:",
    value=st.session_state.user_input,
    height=150
)

# Display example buttons
st.markdown("#### 📝 Example site issues:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌧️ Weather Delay"):
        st.session_state.user_input = example_prompts["weather"]
        st.experimental_rerun()
with col2:
    if st.button("📋 Permit Issue"):
        st.session_state.user_input = example_prompts["permit"]
        st.experimental_rerun()
with col3:
    if st.button("⚠️ Safety Concern"):
        st.session_state.user_input = example_prompts["safety"]
        st.experimental_rerun()

# Reset button
if st.button("🔄 Reset Input"):
    st.session_state.user_input = ""
    st.experimental_rerun()

# Match risks from CSV
def identify_relevant_risks(text, data):
    matches = []
    for _, row in data.iterrows():
        if any(tag.strip().lower() in text.lower() for tag in row['tags'].split(',')):
            matches.append(row)
    return matches

# Generate AI response
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
if st.button("✅ Evaluate Risk") and user_input:
    matched_risks = identify_relevant_risks(user_input, risk_data)
    ai_response = generate_ai_response(user_input, matched_risks)
    st.markdown("### 🧠 Risk Evaluation")
    st.markdown(ai_response)
