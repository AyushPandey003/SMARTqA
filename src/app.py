import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Import backend modules
from backend.ingestion import load_documents, create_vector_db, load_vector_db
from backend.rag import get_llm
from backend.generation import generate_test_cases, generate_selenium_script

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

st.title("Autonomous QA Agent 🤖")
st.markdown("Generate Test Cases and Selenium Scripts from your documentation.")

# Sidebar for Configuration and Ingestion
with st.sidebar:
    st.header("Configuration")
    api_key = os.getenv("GOOGLE_API_KEY","AIzaSyA5GgMqFy6aOG1iywEZjnFQrTxSD4lykJY")
    if not api_key:
        api_key = st.text_input("Enter Google API Key", type="password")
    
    st.header("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Support Documents (PDF, MD, TXT, JSON)", 
        accept_multiple_files=True,
        type=["pdf", "md", "txt", "json"]
    )
    
    uploaded_html = st.file_uploader(
        "Upload Target HTML (checkout.html)", 
        type=["html"]
    )
    
    if st.button("Build Knowledge Base"):
        if not api_key:
            st.error("Please provide a Google API Key.")
        elif not uploaded_files or not uploaded_html:
            st.error("Please upload both support documents and the HTML file.")
        else:
            with st.spinner("Building Knowledge Base..."):
                # Save uploaded files temporarily
                temp_dir = tempfile.mkdtemp()
                file_paths = []
                
                # Save support docs
                for uploaded_file in uploaded_files:
                    path = os.path.join(temp_dir, uploaded_file.name)
                    with open(path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(path)
                
                # Save HTML
                html_path = os.path.join(temp_dir, uploaded_html.name)
                with open(html_path, "wb") as f:
                    f.write(uploaded_html.getbuffer())
                file_paths.append(html_path)
                
                # Ingest
                documents = load_documents(file_paths)
                create_vector_db(documents, api_key)
                st.success("Knowledge Base Built Successfully!")
                st.session_state["html_content"] = uploaded_html.getvalue().decode("utf-8")

# Main Content
if "html_content" not in st.session_state:
    st.info("👈 Please upload documents and build the Knowledge Base to get started.")
else:
    tab1, tab2 = st.tabs(["Test Case Generation", "Selenium Script Generation"])
    
    # Initialize LLM and Vector DB
    if api_key:
        vector_db = load_vector_db(api_key)
        llm = get_llm(api_key)
    
    with tab1:
        st.header("Generate Test Cases")
        requirement = st.text_area("Enter Requirement (e.g., 'Test discount codes')", height=100)
        
        if st.button("Generate Test Cases"):
            if not requirement:
                st.warning("Please enter a requirement.")
            else:
                with st.spinner("Generating Test Cases..."):
                    try:
                        result = generate_test_cases(llm, vector_db, requirement)
                        st.session_state["last_test_cases"] = result
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.header("Generate Selenium Script")
        
        test_case_input = st.text_area(
            "Paste a Test Case (JSON or Text)", 
            value=st.session_state.get("last_test_cases", ""),
            height=200
        )
        
        if st.button("Generate Selenium Script"):
            if not test_case_input:
                st.warning("Please provide a test case.")
            else:
                with st.spinner("Generating Script..."):
                    try:
                        script = generate_selenium_script(
                            llm, 
                            vector_db, 
                            test_case_input, 
                            st.session_state["html_content"]
                        )
                        st.code(script, language="python")
                    except Exception as e:
                        st.error(f"Error: {e}")
