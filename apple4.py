import time
import streamlit as st
import openai
import requests
import os
from openai import OpenAI
import streamlit.components.v1 as components
import random   # (only if you need randomness elsewhere)

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




def search_realtor_listings_serper(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": st.secrets["SERPER_KEY"],  # Add this to secrets.toml
        "Content-Type": "application/json"
    }
    payload = {
        "q": f"site:realtor.ca {query}"  # or use realtor.com depending on region
    }
    response = requests.post(url, headers=headers, json=payload)
    results = response.json().get("organic", [])
    listings = []
    for result in results[:15]:  # Top 5 results
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet", "")
        listings.append(f"🏡 [{title}]({link}) — {snippet}")
    return listings

# Function to generate responses via the Responses API (not completions)
def generate_response(user_input):
    listing_text = ""
    try:
        listing_text = st.session_state.previous_data
    except Exception:
        area = st.session_state.email
        query = f"homes for sale in {area}"
        listings = search_realtor_listings_serper(query)

        listing_text = "\n".join(listings) if listings else "Sorry, I couldn't find listings right now."
        
        st.session_state.previous_data = listing_text
        print(listing_text) 

    # System instructions
    
    instructions = (f"""
    You are a friendly, engaging, and persuasive real estate assistant helping users find their dream home in the mentioned area in Canada.

    Start by greeting the user by name — {st.session_state.name} — and warmly acknowledge the area and price range they are interested in, as described by their input: "{st.session_state.email}".

    Immediately offer a few hand-picked home suggestions that fit their preferences. Include location, estimated price, and a brief highlight (e.g., “spacious backyard,” “close to transit,” or “luxury kitchen”).
    Search Results from Realtor.ca try and answer based on these query data:
    {listing_text}
    
    Make the recommendations sound exciting and personalized and provide them with listings from realtor.ca and other real data sources. After listing 3-5 options of houses in detail, continue the conversation by asking if they'd like to:
    - See more listings,
    - Narrow down preferences (e.g., number of bedrooms or style), or
    - Schedule a virtual showing.
    - Include a real url in each listing

    Keep the tone warm, trustworthy, and enthusiastic. Use persuasive but human-sounding language — like a top-tier agent who’s both knowledgeable and genuinely interested in helping.

    Remember: this is a conversation — not just a static list.
    Start with a list of properties available in the mentioned area within that. When they show the slightest interest in anything tell them to email Danny Leck at dannyl@salefish.app right now also mantion in in the first message.
    """)
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
                /* Hide top-right hamburger menu (≡) */
    #MainMenu {
        visibility: hidden;
    }

    /* Hide 'Made with Streamlit' footer */
    footer {
        visibility: hidden;
    }

    /* Hide GitHub corner icon (if shown by some deployed themes) */
    .stApp a[href^="https://github.com"] {
        display: none;
    }

    /* Optional: Hide all anchor icons beside headers */
    h1 > a:first-child, h2 > a:first-child, h3 > a:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

components.html(
    """
    <div id="emojiWidget"
         style="position:fixed; top:80px; left:50%;
                transform:translateX(-50%);
                font-size:240px; line-height:1;
                z-index:2147483647; user-select:none;">

      <!-- talking face -->
      <span id="face">😀</span>

      <!-- hands -->
      <span id="hand1"
            style="position:absolute; left:-125px; top:46px; font-size:144px;">🤚</span>
      
      <!-- simple arrow only -->
      <span id="arrow"></span>
    </div>

    <style>
      /* hand wave */
      @keyframes wave {0%,100%{transform:rotate(0);}50%{transform:rotate(24deg);} }
      #hand1,#hand2{animation:wave 3s ease-in-out infinite;}
      #hand2{animation-delay:1.5s;}

      /* arrow (triangle) pointing DOWN */
      #arrow{
        position:absolute;
        top:260px;           /* just below the 240 px‑tall face */
        left:50%; transform:translateX(-50%);
        width:0; height:0;
        border-left:24px solid transparent;
        border-right:24px solid transparent;
        border-top:24px solid #ffffff;   /* white arrow tip */
      }
    </style>

    <script>
      /* face swap + random hand shuffle */
      const frames=["🙂","😀"];
      const hands=["🖐️"];

      const face=document.getElementById("face"),
            h1=document.getElementById("hand1"),
            h2=document.getElementById("hand2");

      function rand(a){return a[Math.floor(Math.random()*a.length)];}

      let f=0;
      setInterval(()=>{
        face.textContent=frames[f^=1];     // flip 😃/😮
        h1.textContent=rand(hands);
        h2.textContent=rand(hands);
      },150);   // fast‑talk swap
    </script>
    """,
    height=365,   # iframe occupies no space; widget is fixed
)
# Step 1: Ask for name
if not st.session_state.typed_welcome:
    
    typewriter_effect("Hi, And welcome to the Canadian realtor AI. What should I call you ?", speed=0.02)
    st.session_state.typed_welcome = True

if st.session_state.step == 'ask_name':

    name = st.text_input("Your name:", key="name_input")
    if st.button("Lets Go", key="name_submit"):
        if name:
            st.session_state.name = name
            st.session_state.step = 'ask_email'
            st.rerun()
        else:
            st.warning("Name cannot be empty.")

# Step 2: Ask for email
elif st.session_state.step == 'ask_email':
    st.markdown("### Now can you tell me which areas you are primarily looking to buy in?")
    email = st.text_input("Target Location:")
    if st.button("Next", key="email_submit"):
        if email.strip():
            st.session_state.email = email.strip()
            # Send tracking data
            
            st.session_state.step = 'ask_more'
            st.rerun()
        else:
            st.warning("Location cannot be empty.")
# Step 2: Ask for email
elif st.session_state.step == 'ask_more':
    st.markdown("### And lastly, your expected price range to narrow things down a bit more?")
    more = st.text_input("Price Expectation:")
    if st.button("Start the Conversation", key="email_submit"):
        if more.strip():
            st.session_state.more = more.strip()
            # Send tracking data
            if TRACKING_URL:
                try:
                    requests.post(
                        TRACKING_URL,
                        json={"name": st.session_state.name, "email": st.session_state.email + ',' + st.session_state.more}
                    )
                except Exception:
                    st.error("Failed to send tracking data.")
            st.session_state.step = 'chat'
            st.session_state.messages.append({
                "sender": "bot",
                "text": f"Thanks {st.session_state.name}! Do you want me to start by listing some properties in {st.session_state.email} around {st.session_state.more}?"
            })
            st.rerun()
        else:
            st.warning("Price range cannot be empty.")

# Step 3: Chat interface
else:
    # Render chat history with bubbles
    for msg in st.session_state.messages:
        role = "assistant" if msg["sender"] == "bot" else "user"
        with st.chat_message(role):
            st.write(msg["text"])

    # User input box and Send button
    user_input = st.text_input(
        "You:",
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
            user_input = ""
        else:
            st.warning("Please enter a message before sending.")

