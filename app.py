import os
import streamlit as st
from google import genai
from google.genai import types

# --- Configuration ---
TOPIC = "Network and Server Troubleshooting"
OFF_TOPIC_RESPONSE = f"This chat is strictly about {TOPIC}. Please ask {TOPIC}-related questions."
META_CONVERSATION_RESPONSE = f"This chat is designed to focus solely on {TOPIC}. Please stay on topic."

# The detailed System Instruction based on your requirements
SYSTEM_INSTRUCTION = f"""
You are an expert AI assistant strictly focused on "{TOPIC}".
Your core purpose is to provide fact-based, technical information only related to this topic.

**Strict Topic Enforcement Rules:**
1.  **Allowed Content:** Only provide facts, research, case studies, history, challenges, advancements, policies, laws, scientific research, technologies, or tools directly related to **{TOPIC}**.
2.  **Response Format:**
    * Start the response with an informative title related to the query's topic (e.g., "Diagnosing Server Performance Issues").
    * Use structured, fact-based content with bullet points and headings for readability.
3.  **Off-Topic Handling (CRITICAL):**
    * If a user asks a question that is *entirely* off-topic, or if they insist on an off-topic discussion, you **MUST** respond with: "{OFF_TOPIC_RESPONSE}"
    * If a user asks about *why* they can't ask about other topics (a meta-conversation), you **MUST** respond with: "{META_CONVERSATION_RESPONSE}"
4.  **Mixed Queries:** If a question is partially related to **{TOPIC}** but includes unrelated subjects (e.g., "How do I troubleshoot DNS and what is the best vacation spot?"), you **MUST** focus *only* on the **{TOPIC}** aspect and completely ignore the unrelated part.
5.  **Forbidden Content:** Absolutely NO unrelated topics, other subjects, personal opinions, speculation, entertainment, fictional, or hypothetical discussions.
6.  **Insistence Rule:** If an entirely off-topic question is asked multiple times, ignore it entirely after the first rejection.
"""

# --- Streamlit App Initialization ---

# Set Streamlit Page Config
st.set_page_config(
    page_title=f"{TOPIC} Expert Chatbot",
    page_icon="💻",
    layout="wide"
)

st.title(f"💻 Expert Chat: {TOPIC}")
st.write("I am an AI specialized and strictly focused on **Network and Server Troubleshooting**. Ask me anything technical about the topic!")

# Initialize the Gemini Client
try:
    # Client automatically looks for GEMINI_API_KEY environment variable
    if "GEMINI_API_KEY" not in os.environ:
        st.error("Error: GEMINI_API_KEY environment variable not found. Please set your API key.")
        st.stop()
    client = genai.Client()
except Exception as e:
    st.error(f"Error initializing Gemini Client: {e}")
    st.stop()


# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Gemini Model Interaction Function ---

def generate_response(prompt):
    """Generates a response using the Gemini model with system instructions."""
    
    # Configuration for the Gemini model
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    # Map the history format for the API
    history_for_api = []
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "model"
        history_for_api.append(types.Content(role=role, parts=[types.Part.from_text(message["content"])]))
    
    # Add the current prompt to the history for the API call
    history_for_api.append(types.Content(role="user", parts=[types.Part.from_text(prompt)]))

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history_for_api, # Pass the full history
            config=config,
        )
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"


# --- Main Chat Interface ---

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input field
if prompt := st.chat_input(f"Ask your technical question about {TOPIC}..."):
    # 1. Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI response
    response_text = generate_response(prompt)

    # 3. Add AI response to state and display
    st.session_state.messages.append({"role": "model", "content": response_text})
    with st.chat_message("model"):
        st.markdown(response_text)

# Optional: Clear chat button
if st.button("Clear Chat History"):
    st.session_state["messages"] = []
    st.rerun()
