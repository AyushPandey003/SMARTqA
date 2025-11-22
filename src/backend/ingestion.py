import os
from typing import List
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    BSHTMLLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def load_documents(file_paths: List[str]) -> List[Document]:
    """Loads documents from the given file paths."""
    documents = []
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif ext == ".md":
                loader = UnstructuredMarkdownLoader(file_path)
            elif ext == ".json":
                loader = TextLoader(file_path, encoding="utf-8")
            elif ext == ".html":
                loader = BSHTMLLoader(file_path, bs_kwargs={'features': 'html.parser'})
            else:
                continue
            
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata["source"] = os.path.basename(file_path)
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return documents

def create_vector_db(documents: List[Document], api_key: str = None, db_path: str = "faiss_db"):
    """Creates and saves a FAISS vector database."""
    if not documents:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Using HuggingFace embeddings (local, no API quota limits)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_db = FAISS.from_documents(texts, embeddings)
    vector_db.save_local(db_path)
    return vector_db

def load_vector_db(api_key: str = None, db_path: str = "faiss_db"):
    """Loads an existing FAISS vector database."""
    # Using HuggingFace embeddings (local, no API quota limits)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if os.path.exists(db_path):
        return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    return None
