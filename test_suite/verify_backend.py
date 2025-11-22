import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from backend.ingestion import load_documents, create_vector_db
from backend.rag import get_llm
from backend.generation import generate_test_cases

def verify():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Skipping verification: GOOGLE_API_KEY not found.")
        return

    print("Verifying Ingestion...")
    assets_dir = os.path.join(os.getcwd(), "assets")
    files = [
        os.path.join(assets_dir, "product_specs.md"),
        os.path.join(assets_dir, "ui_ux_guide.txt"),
        os.path.join(assets_dir, "api_endpoints.json"),
        os.path.join(assets_dir, "checkout.html")
    ]
    
    documents = load_documents(files)
    print(f"Loaded {len(documents)} documents.")
    
    print("Creating Vector DB...")
    vector_db = create_vector_db(documents, api_key, db_path="test_faiss_db")
    print("Vector DB created.")
    
    print("Verifying Generation...")
    llm = get_llm(api_key)
    result = generate_test_cases(llm, vector_db, "Test discount codes")
    print("Generated Test Cases:")
    print(result[:200] + "...") # Print first 200 chars
    
    print("Verification Successful!")

if __name__ == "__main__":
    verify()
