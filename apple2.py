import streamlit as st
import openai
import requests

# Configure the page
st.set_page_config(page_title="GTA Home Finder Chatbot", page_icon="🏡")

# Set OpenAI API key & Tracking URL (ensure you have added OPENAI_API_KEY and TRACKING_URL to Streamlit secrets)
openai.api_key = ${{ secrets.GPT_KEY }}
TRACKING_URL = "https://prod-135.westus.logic.azure.com:443/workflows/de75db0162a241b2a0a23ff81b995b27/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=BGPHxgrgadFKgbmtdF0SWXmhkcLtcz9bAiyzUKGBkYw"  # e.g., a webhook endpoint to collect user info

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 'ask_name'
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'loading' not in st.session_state:
    st.session_state.loading = False

# Function to generate GPT-4o responses
def generate_response(user_input):
    messages = [
        {"role": "system", "content": "You are a friendly and persuasive real estate assistant specializing in finding homes in the Greater Toronto Area for users. Encourage them with benefits and detailed suggestions."},
        {"role": "system", "content": f"User name: {st.session_state.name}, email: {st.session_state.email}."}
    ]
    for msg in st.session_state.messages:
        role = "user" if msg["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["text"]})
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

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
            # Send name & email to global tracking endpoint
            if TRACKING_URL:
                try:
                    requests.post(TRACKING_URL, json={
                        "name": st.session_state.name,
                        "email": st.session_state.email
                    })
                except Exception as e:
                    st.error("Failed to send tracking data.")
            st.session_state.step = 'chat'
            st.session_state.messages.append({"sender": "bot", "text": f"Thanks {st.session_state.name}! I'm here to help you find your perfect home in the Greater Toronto Area. What are you looking for today?"})
            st.rerun()
        else:
            st.warning("Email cannot be empty.")

# Step 3: Chat interface
else:
    # Display conversation with chat bubbles
    for msg in st.session_state.messages:
        role = "assistant" if msg["sender"] == "bot" else "user"
        with st.chat_message(role):
            st.write(msg["text"])

    # Input and send controls
    user_input = st.text_input("Your message:", key="user_input", disabled=st.session_state.loading)
    send_disabled = st.session_state.loading
    if st.button("Send", key="send_button", disabled=send_disabled):
        if user_input.strip():
            st.session_state.loading = True
            st.session_state.messages.append({"sender": "user", "text": user_input.strip()})
            # Show loading spinner
            with st.spinner("Thinking..."):
                bot_reply = generate_response(user_input)
            st.session_state.messages.append({"sender": "bot", "text": bot_reply})
            st.session_state.loading = False
            st.rerun()
        else:
            st.warning("Please enter a message before sending.")
