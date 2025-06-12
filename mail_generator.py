import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner

load_dotenv()  # Load variables from .env into environment

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# ✅ Correct API key used here
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

EmailAgent = Agent(
    name="Email Generator",
    instructions="You help write polished, professional emails from short instructions. Make sure the tone matches user input."
)

async def generate_email(prompt):
    try:
        response = await Runner.run_sync(
            EmailAgent,
            input=prompt,
            run_config=config
        )
        return response.final_output
    except Exception as e:
        return f"❌ Error: {e}"

# App configuration
st.set_page_config(page_title="📧 MailCrafter AI", page_icon="📨")

# Session state setup
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Sidebar controls
language = st.sidebar.selectbox("🌐 Language / زبان:", ["English", "اردو"])
toggle = st.sidebar.toggle("🌗 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = toggle

# Labels
labels = {
    "English": {
        "title": "📧 MailCrafter AI",
        "subtitle": "Create polished, professional emails in just a few seconds!",
        "message": "✏️ What's your message or instruction?",
        "tone": "🎯 Choose your email tone:",
        "to": "👤 Recipient Name (To)",
        "from": "🧑‍💼 Your Name (From)",
        "generate": "🚀 Generate Email",
        "warning": "⚠️ Please enter your message or instruction.",
        "loading": "🧠 Thinking... Creating your email...",
        "output": "✅ Your Email:",
        "footer": "Created with ❤️ by Rahat Bano",
        "placeholder": "e.g. Reschedule meeting to Friday at 4 PM",
        "tones": ["Formal", "Friendly", "Apologetic", "Persuasive", "Grateful"]
    },
    "اردو": {
        "title": "📧 میل کرافٹر اے آئی",
        "subtitle": "چند سیکنڈز میں پروفیشنل ای میل تیار کریں!",
        "message": "✏️ اپنا پیغام یا ہدایت لکھیں",
        "tone": "🎯 ای میل کا لہجہ منتخب کریں:",
        "to": "👤 وصول کنندہ کا نام",
        "from": "🧑‍💼 آپ کا نام",
        "generate": "🚀 ای میل تیار کریں",
        "warning": "⚠️ براہ کرم پیغام درج کریں۔",
        "loading": "🧠 سوچ رہا ہے... ای میل تیار ہو رہی ہے...",
        "output": "✅ آپ کی ای میل:",
        "footer": "رحت بانو کی طرف سے محبت کے ساتھ تیار کردہ",
        "placeholder": "مثلاً: میٹنگ کو جمعہ شام 4 بجے منتقل کریں",
        "tones": ["رسمی", "دوستانہ", "معذرت خواہ", "قائل کرنے والا", "شکر گزار"]
    }
}
L = labels[language]

# Theme styles via CSS injection
if st.session_state.dark_mode:
    bg_color = "#0e1117"
    text_color = "#600690"
    input_bg = "#FCFCFD"
    subtitle_color = "#bbbbbb"
else:
    bg_color = "#ffffff"
    text_color = "#6B04FC"
    input_bg = "#f0f2f6"
    subtitle_color = "#555555"

st.markdown(f"""
    <style>
        html, body, .main {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        h1.custom-title {{
            text-align: center;
            color: {text_color} !important;
            font-size: 36px;
            margin-bottom: 0.3em;
        }}
        .subtitle {{
            text-align: center;
            color: {subtitle_color};
            font-size: 18px;
        }}
        textarea, input, .stTextInput > div > div > input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
    </style>
    <h1 class='custom-title'>{L['title']}</h1>
    <p class="subtitle">{L['subtitle']}</p>
    <hr>
""", unsafe_allow_html=True)


# UI inputs
user_prompt = st.text_area(L["message"], placeholder=L["placeholder"], height=100)
tone = st.selectbox(L["tone"], L["tones"])
col1, col2 = st.columns(2)
with col1:
    to_name = st.text_input(L["to"])
with col2:
    from_name = st.text_input(L["from"])

# Generate button
if st.button(L["generate"]):
    if not user_prompt.strip():
        st.warning(L["warning"])
    else:
        with st.spinner(L["loading"]):
            full_prompt = f"Write an email in a {tone.lower()} tone based on this instruction:\n\n{user_prompt}"
            output = asyncio.run(generate_email(full_prompt))

            output = output.replace("[Recipient Name]", to_name if to_name else "Recipient")
            output = output.replace("[Name]", to_name if to_name else "Recipient")
            output = output.replace("[Your Name]", from_name if from_name else "Your Name")
            output = output.replace("[Your Title]", "")

            st.success(L["output"])
            st.write(f"📨 {output}")

# Footer
st.markdown(f"""
    <hr>
    <p style='text-align: center; font-size: 18px; color: {"#f5ecec" if st.session_state.dark_mode else "#888888"}'>
        {L["footer"]}
    </p>
""", unsafe_allow_html=True)
