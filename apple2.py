import streamlit as st
import openai
import requests
import os

# Configure the page
st.set_page_config(page_title="GTA Home Finder Chatbot", page_icon="🏡")

# Set OpenAI API key & Tracking URL (ensure you have added OPENAI_API_KEY and TRACKING_URL to Streamlit secrets)
openai.api_key = os.getenv("GPT_KEY")
TRACKING_URL = "https://prod-135.westus.logic.azure.com:443/workflows/de75db0162a241b2a0a23ff81b995b27/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=BGPHxgrgadFKgbmtdF0SWXmhkcLtcz9bAiyzUKGBkYw"  # e.g., a webhook endpoint to collect user info

# Initialize session state
def init_state():
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
st.title("Find Your Dream Home in the GTA 🏡")

# Step 1: Ask for name
if st.session_state.step == 'ask_name':
    name = st.text_input("Please enter your name:")
    if st.button("Submit Name", key="name_submit"):
        if name.strip():
            st.session_state.name = name.strip()
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
        "Your message:",
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
