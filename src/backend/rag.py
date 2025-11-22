from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(api_key: str, model_name: str = "gemini-2.5-pro"):
    """Initializes the Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
        convert_system_message_to_human=True
    )
