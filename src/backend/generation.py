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
    Generate a robust, self-contained, runnable Selenium script for the following test case.
    
    Test Case:
    {test_case}
    
    HTML Reference (for element selectors only):
    {html_content}
    
    Relevant Documentation Context:
    {context}
    
    CRITICAL INSTRUCTIONS - READ CAREFULLY:
    
    1. **ANALYZE TEST DEPENDENCIES FIRST** (MOST IMPORTANT):
       - Does this test require a logged-in user? → YES: Create a function to register/setup test user BEFORE running the test
       - Does it need data in cart/database? → YES: Create helper functions to set up that data
       - Example: Testing cart features? You MUST create a user first and log them in!
       - Example: Testing checkout? You MUST create user + add items to cart first!
       - Think step-by-step about what needs to exist before your test can run
    
    2. **Test Against Running Flask App**: 
       - Script MUST test against http://127.0.0.1:5000
       - Define: base_url = "http://127.0.0.1:5000"
    
    3. **Do NOT Embed HTML**: 
       - Use HTML reference ONLY to find element selectors (IDs, classes, names, text)
       - Check the HTML carefully for EXACT button text, field names, etc.
    
    4. **Self-Contained & Intelligent**:
       - Script should be runnable standalone with: python script.py
       - Include ALL necessary setup (user creation, login, data preparation)
       - No external dependencies on existing data
    
    5. **Use Explicit Waits**: 
       - Use WebDriverWait with expected_conditions for ALL element interactions
       - Example: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "element_id")))
    
    6. **Accurate Selectors**:
       - Examine the HTML carefully to find correct selectors
       - Use exact text for buttons (e.g., "Sign In" not "Login" if that's what the HTML says)
       - Prefer IDs over XPath when available
    
    7. **Error Handling**: 
       - Include try-except blocks with descriptive messages
       - Print which step failed for easier debugging
    
    8. **Test Reporting**: 
       - Print clear PASS/FAIL messages
       - Show what was tested and the result
    
    9. **Setup/Teardown**: 
       - Initialize driver at start
       - Use try-finally to ensure driver.quit() runs
    
    10. **Required Imports**:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        import uuid  # For generating unique test data
        import time  # For occasional sleeps if needed
    
    11. **No Test Frameworks**: 
        - NO pytest, unittest, or test classes
        - Use simple: if __name__ == "__main__": block
    
    12. **Output Format**: 
        - Output ONLY Python code
        - NO markdown formatting like ```python
        - NO explanatory text, just code
    
    EXAMPLE STRUCTURE for Login-Dependent Tests:
    ```
    # Imports
    import uuid
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Helper function to register user
    def setup_test_user(driver):
        # Try to login first to check if user exists
        # If not, register the user
        pass
    
    # Helper function to login
    def login_user(driver, username, password):
        driver.get(f"{{BASE_URL}}/login")
        # Fill form and submit
        pass
    
    # Main execution
    if __name__ == "__main__":
        driver = None
        try:
            driver = webdriver.Chrome()
            
            # STEP 1: Setup prerequisites
            setup_test_user(driver)
            
            # STEP 2: Run the actual test
            # ... test logic here ...
            
            print("PASS: Test completed successfully")
        except Exception as e:
            print(f"FAIL: {{e}}")
        finally:
            if driver:
                driver.quit()
    ```
    
    Now generate the complete, runnable script for the given test case.
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
    
    result = rag_chain.invoke(test_case)
    # Clean up markdown formatting if present
    return result.replace("```python", "").replace("```", "").strip()
