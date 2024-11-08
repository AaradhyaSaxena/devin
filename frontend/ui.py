import streamlit as st
import requests

BASE_URL = "http://your-api-url.com"  # Replace with your actual API URL

st.title("Simple Chat UI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("What's your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Send request to API
    with st.spinner("Thinking..."):
        try:
            response = requests.post(f"{BASE_URL}/chat", json={"query": prompt})
            response.raise_for_status()
            answer = response.json()["response"]
        except requests.RequestException as e:
            answer = f"Error: Unable to get response from API. {str(e)}"

    # Display assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)