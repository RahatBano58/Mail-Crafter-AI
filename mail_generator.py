from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner
import streamlit as st
from dotenv import load_dotenv
import os
import asyncio

if "email_history" not in st.session_state:
    st.session_state.email_history = []
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please ensure it is defined in your .env file")


external_client = AsyncOpenAI(
    api_key=API_KEY,
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
EnhancerAgent = Agent(
    name="Email Enhancer",
    instructions="You improve existing emails to sound more professional, clear, and polite without changing the original intent."
)


async def generate_email(prompt):
    try:
        response = await Runner.run(
            EmailAgent,
            input=prompt,
            run_config=config
        )
        return response.final_output
    except Exception as e:
        return f"❌ Error: {e}"


async def enhance_email(prompt):
    try:
        response = await Runner.run(EnhancerAgent, input=prompt, run_config=config)
        return response.final_output
    except Exception as e:
        return f"❌ Error: {e}"


st.set_page_config(page_title="MailCrafter AI", page_icon="📧")
st.sidebar.title("📬 MailCrafter AI")
page = st.sidebar.radio(
    "Select Feature", ["📧 Generate Email", "✨ Enhance Email"])
st.sidebar.markdown("## 📜 Email History")

# Tabs not supported in sidebar, so we'll just separate by type
generated_items = [
    item for item in st.session_state.email_history if item['type'] == "Generated"]
enhanced_items = [
    item for item in st.session_state.email_history if item['type'] == "Enhanced"]

# 📧 Generated Emails
if generated_items:
    st.sidebar.markdown("### 📧 Generated Emails")
    for i, item in enumerate(reversed(generated_items), 1):
        st.sidebar.markdown(f"**{i}.** {item['prompt'][:30]}...")
        if st.sidebar.button(f"View Generated {i}", key=f"gen_{i}"):
            # store in session for viewing below
            st.session_state["viewed_email"] = item
else:
    st.sidebar.write("No generated emails yet.")

# ✨ Enhanced Emails
if enhanced_items:
    st.sidebar.markdown("### ✨ Enhanced Emails")
    for i, item in enumerate(reversed(enhanced_items), 1):
        st.sidebar.markdown(f"**{i}.** {item['prompt'][:30]}...")
        if st.sidebar.button(f"View Enhanced {i}", key=f"enh_{i}"):
            st.session_state["viewed_email"] = item
else:
    st.sidebar.write("No enhanced emails yet.")


if "viewed_email" in st.session_state:
    email = st.session_state["viewed_email"]
    st.markdown("## 📬 Email Detail")
    st.markdown(f"**Type:** {email['type']}")
    st.markdown(f"**Prompt:**")
    st.code(email['prompt'], language="markdown")
    st.markdown("**Generated Email:**")
    st.code(email['email'], language="markdown")


st.title(page)

# Streamlit UI

if page == "📧 Generate Email":
    user_prompt = st.text_area(
        "✏️ What's your message? (e.g. reschedule meeting to Monday at 4pm))", height=100)
    tone = st.selectbox("🎯 Choose the tone of your email:", [
        "Formal", "Friendly", "Apologetic", "Persuasive", "Grateful",
        "Assertive", "Confident", "Encouraging", "Tactful", "Professional",
        "Sympathetic", "Urgent", "Casual", "Instructive"
    ])
    to_name = st.text_input("👤 Recipient Name (To)")
    from_name = st.text_input("🧑‍💼 Your Name (From)")

    if st.button("Generate Email"):
        if not user_prompt.strip():
            st.warning("Please write a message first.")
        else:
            with st.spinner("Generating your email..."):
                full_prompt = f"Write an email in a {tone.lower()} tone based on this instruction:\n\n{user_prompt}"
                output = asyncio.run(generate_email(full_prompt))
                output = output.replace(
                    "[Recipient Name]", to_name or "Recipient")
                output = output.replace("[Name]", to_name or "Recipient")
                output = output.replace(
                    "[Your Name]", from_name or "Your Name")
                output = output.replace("[Your Title]", "")

                st.session_state.email_history.append({
                    "type": "Generated",
                    "prompt": user_prompt,
                    "tone": tone,
                    "email": output
                })

                st.subheader("✅ Your Email:")
                st.success(output)

# === Email Enhancer Page ===
elif page == "✨ Enhance Email":
    original_email = st.text_area(
        "📥 Paste your existing email here", height=200)

    if st.button("Enhance Email"):
        if not original_email.strip():
            st.warning("Please paste an email first.")
        else:
            with st.spinner("Enhancing your email..."):
                enhance_prompt = f"Please improve this email to be more professional, polite, and well-structured:\n\n{original_email}"
                enhanced = asyncio.run(enhance_email(enhance_prompt))

                st.session_state.email_history.append({
                    "type": "Enhanced",
                    "prompt": original_email,
                    "tone": "N/A",
                    "email": enhanced
                })
                st.subheader("✨ Enhanced Email:")
                st.success(enhanced)

st.markdown("---")
st.markdown("📬 **MailCrafter AI** &copy; 2025 | Built with ❤️ using Streamlit")
st.markdown(
    "📧 Contact: `rahatbano142@gmail.com` | 🔗 [GitHub](https://github.com/RahatBano58)")
