from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def generate_test_cases(llm, vector_db, requirement: str):
    """Generates test cases based on the requirement and knowledge base."""
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    
    template = """You are an expert QA engineer. Based on the following context from project documentation, 
    generate comprehensive test cases for the given requirement.
    
    Context:
    {context}
    
    Requirement: {requirement}
    
    Output Format:
    Provide a JSON list of test cases. Each test case should have:
    - Test_ID
    - Feature
    - Test_Scenario
    - Expected_Result
    - Grounded_In (Source document filename)
    
    Ensure no hallucinations. Only use features mentioned in the context.
    """
    
    prompt = PromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content + f"\n(Source: {doc.metadata.get('source', 'unknown')})" for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "requirement": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(requirement)

def generate_selenium_script(llm, vector_db, test_case: str, html_content: str):
    """Generates a Selenium script for a specific test case."""
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    template = """You are an expert Selenium Python automation engineer.
    Generate a robust, runnable Selenium script for the following test case.
    
    Test Case:
    {test_case}
    
    Target HTML Content:
    {html_content}
    
    Relevant Documentation Context:
    {context}
    
    Instructions:
    1. Use `webdriver.Chrome()`.
    2. Use explicit waits (`WebDriverWait`) for element interaction.
    3. Use precise selectors based on the provided HTML (IDs, Classes, Names).
    4. Include comments explaining the steps.
    5. Handle potential errors gracefully.
    6. Do NOT use pytest, unittest, or classes. Generate a simple standalone script with a `if __name__ == "__main__":` block.
    7. Ensure all imports are correct and necessary. Do NOT import built-in Python exceptions (like AssertionError) from selenium modules.
    8. Output ONLY the Python code, no markdown formatting like ```python.
    """
    
    prompt = PromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "test_case": RunnablePassthrough(), "html_content": lambda x: html_content}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(test_case)
