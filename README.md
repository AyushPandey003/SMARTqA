# Autonomous QA Agent

## Overview
This project is an intelligent, autonomous QA agent capable of constructing a "testing brain" from project documentation. It ingests support documents (product specs, UI/UX guides, etc.) and the target HTML structure to generate comprehensive test cases and executable Selenium scripts.

## Features
- **Knowledge Base Ingestion**: Upload PDF, TXT, MD, JSON, and HTML files to build a vector database (FAISS).
- **Test Case Generation**: Uses RAG (Retrieval-Augmented Generation) to produce grounded test cases.
- **Selenium Script Generation**: Converts selected test cases into runnable Python Selenium scripts.
- **Streamlit UI**: User-friendly interface for all operations.

## Setup Instructions

### Prerequisites
- Python 3.8+
- A Google Gemini API Key.

### Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
The system uses **Google Gemini**.
- Set the `GOOGLE_API_KEY` environment variable.
  ```bash
  set GOOGLE_API_KEY=your_api_key_here
  ```

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. **Ingest Documents**:
   - Go to the sidebar.
   - Upload `assets/product_specs.md`, `assets/ui_ux_guide.txt`, `assets/api_endpoints.json`.
   - Upload `assets/checkout.html`.
   - Click "Build Knowledge Base".
3. **Generate Test Cases**:
   - Go to the "Test Case Generation" tab.
   - Enter a requirement (e.g., "Test discount codes").
   - Click "Generate".
4. **Generate Scripts**:
   - Go to the "Selenium Script Generation" tab.
   - Select or paste a test case.
   - Click "Generate Selenium Script".

## Project Structure
- `app.py`: Main Streamlit application.
- `backend/`: Core logic for ingestion, RAG, and generation.
- `assets/`: Sample project files for testing.
- `faiss_db/`: Local vector database storage.
