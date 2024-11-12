import streamlit as st
import pandas as pd
import requests
import json

# Load config
try:
    with open('../config/config.json') as f:
        config = json.load(f)
        BASE_URL = config.get('BASE_URL', "http://127.0.0.1:5001")
except:
    BASE_URL = "http://127.0.0.1:5001"

st.title("PACE")

# Initialize session state for file lists if not exists
if "file_list" not in st.session_state:
    try:
        df = pd.read_csv('data/repo_content.csv')
        st.session_state.file_list = df['Path'].tolist()
    except Exception as e:
        st.error(f"Error reading file list: {str(e)}")
        st.session_state.file_list = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create the input form
with st.form("code_generation_form"):
    # Query input
    query = st.text_area("Enter your query:", height=100)
    
    # Reference files selection
    reference_files = st.multiselect(
        "Select reference files:",
        options=st.session_state.file_list,
        default=[]
    )
    
    # Submit button
    submitted = st.form_submit_button("Generate Code")

# Handle form submission
if submitted and query:
    # Prepare the request payload
    payload = {
        "query": query,
        "reference_filepaths": reference_files
    }
    
    # Add user query to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": f"""Query: {query}
            Reference Files: {', '.join(reference_files) if reference_files else 'None'}"""
    })
    
    with st.chat_message("user"):
        st.write(st.session_state.messages[-1]["content"])
    
    # Send request to API
    with st.spinner("Generating code..."):
        try:
            response = requests.post(f"{BASE_URL}/generate_code", json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract code from response
            if "code" in result:
                answer = result["code"]
                
            else:
                answer = "Error: Unexpected response format from API"
                
        except requests.RequestException as e:
            answer = f"Error: Unable to get response from API. {str(e)}"
    
    # Display assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        try:
            response_data = json.loads(answer)
            # st.write('items:', response_data.items())
            
            if "explanation" in response_data:
                st.markdown(response_data["explanation"])
            if "files" in response_data:
                for filename, code in response_data["files"].items():
                    st.markdown(f"**File: `{filename}`**")
                    st.code(code, language="python")
                    
        except json.JSONDecodeError:
            st.write(answer)

# Display chat history
if st.session_state.messages:
    st.divider()
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])