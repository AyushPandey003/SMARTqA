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

# Custom CSS for skeleton loading
st.markdown("""
<style>
    @keyframes skeleton-pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    
    .skeleton {
        animation: skeleton-pulse 1.5s ease-in-out infinite;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        border-radius: 4px;
    }
    
    .skeleton-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .skeleton-line {
        height: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
    
    .skeleton-line.short { width: 30%; }
    .skeleton-line.medium { width: 60%; }
    .skeleton-line.long { width: 90%; }
    
    .skeleton-code {
        background: #282c34;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
    }
    
    .skeleton-code-line {
        height: 16px;
        margin: 6px 0;
        border-radius: 3px;
        background: linear-gradient(90deg, #3a3f4b 25%, #4a4f5b 50%, #3a3f4b 75%);
        background-size: 200% 100%;
    }
</style>
""", unsafe_allow_html=True)

def render_skeleton_progress():
    """Render skeleton for knowledge base building progress."""
    return """
    <div style="padding: 20px;">
        <div class="skeleton-card">
            <div class="skeleton skeleton-line medium"></div>
            <div style="height: 8px;"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line medium"></div>
        </div>
        <div class="skeleton-card">
            <div class="skeleton skeleton-line short"></div>
            <div style="height: 8px;"></div>
            <div class="skeleton skeleton-line long"></div>
        </div>
        <div class="skeleton-card">
            <div class="skeleton skeleton-line medium"></div>
            <div style="height: 8px;"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line short"></div>
        </div>
    </div>
    """

def render_skeleton_cards():
    """Render skeleton cards for test case generation."""
    return """
    <div style="padding: 20px;">
        <div class="skeleton-card">
            <div class="skeleton skeleton-line short"></div>
            <div style="height: 12px;"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line medium"></div>
            <div class="skeleton skeleton-line long"></div>
        </div>
        <div class="skeleton-card">
            <div class="skeleton skeleton-line short"></div>
            <div style="height: 12px;"></div>
            <div class="skeleton skeleton-line medium"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line medium"></div>
        </div>
        <div class="skeleton-card">
            <div class="skeleton skeleton-line short"></div>
            <div style="height: 12px;"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line long"></div>
            <div class="skeleton skeleton-line short"></div>
        </div>
    </div>
    """

def render_skeleton_code():
    """Render skeleton for code generation."""
    return """
    <div class="skeleton-code">
        <div class="skeleton skeleton-code-line" style="width: 40%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 60%;"></div>
        <div style="height: 8px;"></div>
        <div class="skeleton skeleton-code-line" style="width: 75%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 85%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 70%;"></div>
        <div style="height: 8px;"></div>
        <div class="skeleton skeleton-code-line" style="width: 55%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 80%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 65%;"></div>
        <div style="height: 8px;"></div>
        <div class="skeleton skeleton-code-line" style="width: 90%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 70%;"></div>
        <div class="skeleton skeleton-code-line" style="width: 60%;"></div>
    </div>
    """

st.title("Autonomous QA Agent 🤖")
st.markdown("Generate Test Cases and Selenium Scripts from your documentation.")

# Sidebar for Configuration and Ingestion
with st.sidebar:
    st.header("Configuration")
    api_key = os.getenv("GOOGLE_API_KEY","")
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
            # Create placeholder for skeleton loading
            loading_placeholder = st.empty()
            
            # Show skeleton while loading
            loading_placeholder.markdown(render_skeleton_progress(), unsafe_allow_html=True)
            
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
            
            # Clear skeleton and show success
            loading_placeholder.empty()
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
                # Create placeholder for skeleton loading
                loading_placeholder = st.empty()
                
                # Show skeleton while loading
                loading_placeholder.markdown(render_skeleton_cards(), unsafe_allow_html=True)
                
                try:
                    result = generate_test_cases(llm, vector_db, requirement)
                    st.session_state["last_test_cases"] = result
                    
                    # Clear skeleton and show result
                    loading_placeholder.empty()
                    st.markdown(result)
                except Exception as e:
                    loading_placeholder.empty()
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
                # Create placeholder for skeleton loading
                loading_placeholder = st.empty()
                
                # Show skeleton while loading
                loading_placeholder.markdown(render_skeleton_code(), unsafe_allow_html=True)
                
                try:
                    script = generate_selenium_script(
                        llm, 
                        vector_db, 
                        test_case_input, 
                        st.session_state["html_content"]
                    )
                    
                    # Clear skeleton and show result
                    loading_placeholder.empty()
                    st.code(script, language="python")
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"Error: {e}")
