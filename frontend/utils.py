import streamlit as st
import requests

def handle_merge_request(filename, code, explanation, base_url):
    """Handle the merge request for a specific file.
    
    Args:
        filename (str): Name of the file to merge changes into
        code (str): The suggested code changes
        explanation (str): Explanation of the changes
        base_url (str): Base URL for the API
        
    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        merge_payload = {
            "filename": filename,
            "suggested_changes": code,
            "explanation": explanation
        }
        merge_response = requests.post(
            f"{base_url}/merge_code",
            json=merge_payload
        )
        merge_response.raise_for_status()
        return True
    except requests.RequestException as e:
        st.error(f"Error merging changes: {str(e)}")
        return False

def display_code_block(filename, code, explanation, base_url):
    """Display a code block with merge functionality.
    
    Args:
        filename (str): Name of the file
        code (str): The code to display
        explanation (str): Explanation of the changes
        base_url (str): Base URL for the API
    """
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**File: `{filename}`**")
    with col2:
        if st.button("Merge Changes", key=f"merge_{filename}"):
            with st.spinner("Merging changes..."):
                if handle_merge_request(filename, code, explanation, base_url):
                    st.success(f"Changes merged successfully for {filename}")
    
    st.code(code, language="python")

def display_code_changes(filename, code_data):
    """Helper function to display code changes in a readable format"""
    # Create columns for the header and merge button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### 📄 {filename}")
    with col2:
        if st.button("Merge All Changes", key=f"merge_all_{filename}"):
            with st.spinner("Merging changes..."):
                # Combine all changes into a single code block
                combined_code = "\n".join(
                    change.get("content", "").strip()
                    for change in code_data.get("changes", [])
                )
                # Get combined explanation
                combined_explanation = "\n".join(
                    change.get("explanation", "")
                    for change in code_data.get("changes", [])
                    if change.get("explanation")
                )
                if handle_merge_request(filename, combined_code, combined_explanation, st.session_state.base_url):
                    st.success(f"Changes merged successfully for {filename}")
    
    if "changes" in code_data:
        for change in code_data["changes"]:
            # Display change type with appropriate emoji
            change_type = change.get("type", "")
            emoji = {
                "addition": "➕",
                "deletion": "➖",
                "modification": "🔄"
            }.get(change_type, "ℹ️")
            
            st.markdown(f"{emoji} **Line {change.get('line', '')}**")
            
            # Display the code content in a code block
            content = change.get("content", "").strip()
            st.code(content, language=filename.split('.')[-1])
            
            # Display explanation if available
            if explanation := change.get("explanation"):
                st.info(explanation)
            
            st.divider()

def format_explanation(explanation_data):
    """Helper function to format explanation sections with better styling"""
    if "problem_analysis" in explanation_data:
        st.markdown("### 🔍 Problem Analysis")
        st.info(explanation_data["problem_analysis"])
    
    if "solution_overview" in explanation_data:
        st.markdown("### 💡 Solution Overview")
        st.success(explanation_data["solution_overview"])
    
    if "considerations" in explanation_data:
        st.markdown("### ⚖️ Key Considerations")
        for consideration in explanation_data["considerations"]:
            st.markdown(f"- {consideration}")
    
    if "risks" in explanation_data:
        st.markdown("### ⚠️ Potential Risks")
        for risk in explanation_data["risks"]:
            st.write("- " + risk)