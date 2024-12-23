import streamlit as st
import pandas as pd
import requests
import json
from utils import display_code_block, handle_merge_request, format_explanation

# Load config
try:
    with open('../config/config.json') as f:
        config = json.load(f)
        BASE_URL = config.get('BASE_URL')
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
            if isinstance(answer, str):
                response_data = json.loads(answer)
            else:
                response_data = answer
            
            # Create tabs for better organization
            explanation_tab, changes_tab, testing_tab = st.tabs([
                "📝 Explanation", 
                "🔄 Code Changes", 
                "🧪 Testing"
            ])
            
            with explanation_tab:
                if "explanation" in response_data:
                    explanation = response_data["explanation"]
                    if isinstance(explanation, str):
                        try:
                            explanation_data = json.loads(explanation)
                            format_explanation(explanation_data)
                        except json.JSONDecodeError:
                            st.markdown(explanation)
                    else:
                        format_explanation(explanation)
            
            with changes_tab:
                if "files" in response_data:
                    for filename, code in response_data["files"].items():
                        st.markdown(f"### 📄 {filename}")
                        display_code_block(
                            filename=filename,
                            code=code,
                            explanation=response_data.get("explanation", ""),
                            base_url=BASE_URL
                        )
            
            with testing_tab:
                if "testing" in response_data:
                    testing = response_data["testing"]
                    if "required_tests" in testing:
                        st.markdown("### Required Tests")
                        for test in testing["required_tests"]:
                            st.markdown(f"- {test}")
                    if "validation_steps" in testing:
                        st.markdown("### Validation Steps")
                        for step in testing["validation_steps"]:
                            st.markdown(f"- {step}")
                        
        except json.JSONDecodeError:
            st.error("Failed to parse response")
            st.code(answer)

# Display chat history
if st.session_state.messages:
    st.divider()
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])