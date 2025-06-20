import time
import streamlit as st
import openai
import requests
import os
from openai import OpenAI

# Configure the page
st.set_page_config(page_title="Canadian Home Finder Chatbot", page_icon="🏡")

# Set OpenAI API key & Tracking URL (ensure you have added OPENAI_API_KEY and TRACKING_URL to Streamlit secrets)
key = st.secrets["GPT_KEY"]
TRACKING_URL = "https://prod-135.westus.logic.azure.com:443/workflows/de75db0162a241b2a0a23ff81b995b27/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=BGPHxgrgadFKgbmtdF0SWXmhkcLtcz9bAiyzUKGBkYw"  # e.g., a webhook endpoint to collect user info
client = OpenAI(api_key=key)
# Initialize session state
def init_state():
    if 'typed_welcome' not in st.session_state:
        st.session_state.typed_welcome = False
    if 'step' not in st.session_state:
        st.session_state.step = 'ask_name'
    defaults = {
        'step': 'ask_name',
        'name': '',
        'email': '',
        'messages': [],
        'loading': False
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def typewriter_effect(text, speed=0.5):
    if st.session_state.step == 'ask_name':
        container = st.empty()
        output = ""
        for char in text:
            output += char
            container.markdown(f"### {output}")
            time.sleep(speed)
    else:
        pass

init_state()

# Function to generate responses via the Responses API (not completions)
def generate_response(user_input):
    # System instructions
    instructions = (
        "You are a friendly and persuasive real estate assistant specializing in finding homes in the "
        "Greater Toronto Area for users. Encourage them with benefits and detailed suggestions."
    )
    # Build a flat conversation prompt
    conversation_lines = []
    for m in st.session_state.messages:
        speaker = "User" if m["sender"] == "user" else "Assistant"
        conversation_lines.append(f"{speaker}: {m['text']}")
    conversation = "\n".join(conversation_lines)
    prompt = f"{conversation}\nUser: {user_input}\nAssistant:"

    # Call the Responses API instead of chat completions
    response = client.responses.create(
        model="gpt-4o",
        instructions=instructions,
        input=prompt
    )
    return response.output_text.strip()

# App title
st.title("🍁 Find Your Dream Home Now 🏡")
st.markdown("""
<style>
/* ---------- BACKGROUND BASE ---------- */
.st-emotion-cache-13k62yr {
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #1c1c1c, #1a1a1a, #2e1f3d);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: #f5f5f5;
    overflow-x: hidden;
}

/* Animated color shift for the gradient */
@keyframes gradientShift {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
            

/* ---------- GLOWING FLOATING PARTICLES (MAPLE THEME) ---------- */
.st-emotion-cache-13k62yr::after {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    background-image:
        radial-gradient(circle, rgba(255,102,102,0.1) 3%, transparent 60%),
        radial-gradient(circle, rgba(255,235,59,0.06) 2%, transparent 50%),
        radial-gradient(circle, rgba(255,102,102,0.1) 4%, transparent 70%);
    background-size: 200px 200px;
    animation: floatGlow 20s linear infinite;
    z-index: -1;
}

@keyframes floatGlow {
    0% { background-position: 0 0, 100px 200px, 200px 100px; }
    50% { background-position: 300px 400px, 400px 300px, 500px 100px; }
    100% { background-position: 0 0, 100px 200px, 200px 100px; }
}

/* ---------- HEADINGS ---------- */
h1, h2, h3 {
    color: #ffe0b2;
    text-shadow: 2px 2px 6px rgba(255, 102, 102, 0.5);
}

/* ---------- INPUTS ---------- */
input, textarea {
    background-color: #1c1c1c !important;
    color: #fefefe !important;
    border: 1px solid #5a3f5c !important;
    border-radius: 6px !important;
    box-shadow: 0 0 10px #ff704355;
    padding: 0.5rem !important;
    transition: 0.3s ease-in-out;
}

 input:focus, textarea:focus {
    box-shadow: 0 0 15px #ffccbcaa !important;
    border-color: #5a3f5c !important;
    outline: none !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    background: linear-gradient(to right, #5a3f5c, #812c7a);
    color: #fdfdfd;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-size: 1rem;
    box-shadow: 0 0 12px #812c7a88;
    transition: all 0.3s ease;
}

/* ---------- BUTTON HOVER ---------- */
.stButton > button:hover {
    background: linear-gradient(to right, #812c7a, #5a3f5c);
    box-shadow: 0 0 18px #ff99cc88, 0 0 6px #ff66cc55;
    transform: scale(1.05);
}

/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background-color: #8B1A1A;
    border-radius: 4px;
}
::-webkit-scrollbar-track {
    background-color: #2e2e2e;
}
</style>
""", unsafe_allow_html=True)
# Step 1: Ask for name
if st.session_state.step == 'ask_name' and not st.session_state.typed_welcome:
    
    typewriter_effect("Welcome to the Canadian realtor AI. Can you please let me know of your name to confirm you got an invite to our brand new application beta ?", speed=0.02)
    st.session_state.typed_welcome = True

    name = st.text_input("Name here:", key="name_input")
    if st.button("Lets Go", key="name_submit"):
        print("DEBUG: button fired, name =", repr(name))
        if name:
            st.session_state.name = name
            st.session_state.step = 'ask_email'
            st.rerun()
        else:
            st.warning("Name cannot be empty.")

# Step 2: Ask for email
elif st.session_state.step == 'ask_email':
    email = st.text_input("Please enter your email:")
    if st.button("Submit Email", key="email_submit"):
        if email.strip():
            st.session_state.email = email.strip()
            # Send tracking data
            if TRACKING_URL:
                try:
                    requests.post(
                        TRACKING_URL,
                        json={"name": st.session_state.name, "email": st.session_state.email}
                    )
                except Exception:
                    st.error("Failed to send tracking data.")
            st.session_state.step = 'chat'
            st.session_state.messages.append({
                "sender": "bot",
                "text": f"Thanks {st.session_state.name}! I'm here to help you find your perfect home in the Greater Toronto Area. What are you looking for today?"
            })
            st.rerun()
        else:
            st.warning("Email cannot be empty.")

# Step 3: Chat interface
else:
    # Render chat history with bubbles
    for msg in st.session_state.messages:
        role = "assistant" if msg["sender"] == "bot" else "user"
        with st.chat_message(role):
            st.write(msg["text"])

    # User input box and Send button
    user_input = st.text_input(
        "Lets start chatting shall we ?",
        key="user_input",
        disabled=st.session_state.loading
    )
    if st.button("Send", key="send_button", disabled=st.session_state.loading):
        if user_input.strip():
            st.session_state.loading = True
            st.session_state.messages.append({"sender": "user", "text": user_input.strip()})
            with st.spinner("Thinking..."):
                reply = generate_response(user_input)
            st.session_state.messages.append({"sender": "bot", "text": reply})
            st.session_state.loading = False
            st.rerun()
        else:
            st.warning("Please enter a message before sending.")

