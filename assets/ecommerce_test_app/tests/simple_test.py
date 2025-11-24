import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_test():
    print("Setting up Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Register
        print("Navigating to Register page...")
        driver.get(f"{base_url}/register")
        
        unique_id = str(uuid.uuid4())[:8]
        username = f"user_{unique_id}"
        email = f"user_{unique_id}@example.com"
        password = "password123"
        
        print(f"Registering user: {username}")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        
        # Click Register button (it's a button in the form, usually type submit)
        # Checking register.html would confirm, but usually it's the only button or input[type=submit]
        # I'll use a generic selector for the submit button in the form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Should redirect to login
        print("Waiting for redirect to login...")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        
        print("Logging in...")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Should be at index
        print("Waiting for redirect to index...")
        WebDriverWait(driver, 10).until(EC.url_to_be(f"{base_url}/"))
        print("Login successful.")
        
        # 2. Add to cart
        print("Adding product to cart...")
        # Find the first "Add to Cart" button
        add_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='add_to_cart']"))
        )
        add_btn.click()
        
        # Should flash message and redirect to index (or stay on index with flash)
        # We can just wait a bit or check for the flash message if we want, but let's just proceed to cart
        time.sleep(1)
        
        # 3. Go to Cart
        print("Going to cart...")
        driver.get(f"{base_url}/cart")
        
        # 4. Checkout
        print("Checking out...")
        checkout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form[action*='checkout'] button"))
        )
        checkout_btn.click()
        
        # 5. Assert Success
        print("Verifying order...")
        # The flash message "Order placed successfully!" should be present
        success_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Order placed successfully')]"))
        )
        print("Test Passed: Order placed successfully!")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        # driver.save_screenshot("error_screenshot.png") # Optional
        raise e
    finally:
        print("Closing driver...")
        driver.quit()

if __name__ == "__main__":
    run_test()
