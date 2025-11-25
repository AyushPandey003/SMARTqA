import uuid
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"
WAIT_TIMEOUT = 10

# --- Helper Functions for Test Prerequisites ---

def register_and_login(driver, user_details):
    """
    Registers a new user and logs them in.
    Verifies successful registration and login.
    """
    username = user_details['username']
    email = user_details['email']
    password = user_details['password']
    
    # --- Registration ---
    print(f"INFO: Attempting to register a new user: {username}")
    driver.get(f"{BASE_URL}/register")
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        # Template uses 'name' attributes instead of ids; use By.NAME for robustness
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        # Use a robust selector for the submit button (type='submit') instead of exact visible text
        try:
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except Exception:
            # Dump a small debug HTML snapshot to help diagnose selector issues
            debug_file = f"register_page_debug_{username}.html"
            with open(debug_file, "w", encoding="utf-8") as fh:
                fh.write(driver.page_source)
            print(f"WARN: Could not find submit button by type; saved page HTML to {debug_file}")
            raise

        # After successful registration the app redirects to the login page
        wait.until(EC.url_contains("/login"))
        print("INFO: Registration successful (redirected to login).")
    except TimeoutException:
        raise Exception(f"FAIL: Could not register user '{username}'. Registration page might not have loaded or confirmation redirect not seen.")

    # --- Login ---
    print(f"INFO: Attempting to log in as: {username}")
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        driver.get(f"{BASE_URL}/login")
        # Login form also uses name attributes
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()

        # Verify login success by checking for the "Logout" link
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
        print("INFO: Login successful.")
    except TimeoutException:
        raise Exception(f"FAIL: Could not log in as user '{username}'. Login failed or redirect was unsuccessful.")

def add_item_to_cart(driver):
    """
    Navigates to the home page, clicks on a product, adds it to the cart,
    and verifies the action was successful.
    """
    print("INFO: Adding an item to the cart...")
    driver.get(BASE_URL)
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        
        # Click on the first product to go to detail page
        print("INFO: Navigating to product detail page...")
        product_link = wait.until(EC.element_to_be_clickable((By.XPATH, "(//a[contains(@href, '/product/')])[1]")))
        product_link.click()
        
        # Find the "Add to Cart" link on the product detail page
        # Note: It is an <a> tag styled as a button
        add_to_cart_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Add to Cart')]")))
        add_to_cart_link.click()

        # Verify success flash message (look for the text anywhere on the page)
        # Using contains(., ...) to check text content of the element including descendants
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Item added to cart')]")))

        # Navigate to the cart page and ensure it contains items (not the 'Your cart is empty' message)
        driver.get(f"{BASE_URL}/cart")
        time.sleep(1)
        if "Your cart is empty" in driver.page_source:
            raise Exception("Cart appears to be empty after adding an item.")
        print("INFO: Item successfully added to cart.")
            
    except TimeoutException:
        raise Exception("FAIL: Could not add item to cart. Product link, 'Add to Cart' button, or success message not found.")
    except Exception as e:
        raise Exception(f"FAIL: An error occurred while adding item to cart: {e}")

# --- Main Test Execution ---

def run_checkout_test(driver):
    """
    Executes the full checkout process test case.
    """
    print("\n--- Test Case: Full Checkout Process ---")
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # 1. Navigate to Cart and Proceed to Checkout
    print("INFO: Navigating to cart and proceeding to checkout...")
    driver.get(f"{BASE_URL}/cart")
    try:
        # The 'Proceed to Checkout' button is a <button> element, not an <a> tag
        checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed to Checkout')]")))
        checkout_button.click()
    except TimeoutException:
        raise Exception("FAIL: Could not find 'Proceed to Checkout' button on the cart page.")

    # 2. Fill Shipping Address
    print("INFO: Filling out shipping address...")
    try:
        # Wait for a key element on the checkout page to ensure it's loaded
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), '1. Shipping Address')]")))
        
        # Using XPath to locate inputs based on their associated label text for robustness
        full_name_input = driver.find_element(By.XPATH, "//p[text()='Full Name']/following-sibling::input")
        street_input = driver.find_element(By.XPATH, "//p[text()='Street Address']/following-sibling::input")
        city_input = driver.find_element(By.XPATH, "//p[text()='City']/following-sibling::input")
        state_input = driver.find_element(By.XPATH, "//p[text()='State']/following-sibling::input")
        zip_input = driver.find_element(By.XPATH, "//p[text()='ZIP Code']/following-sibling::input")

        full_name_input.clear()
        full_name_input.send_keys("Test User")
        
        street_input.clear()
        street_input.send_keys("456 Automation Lane")
        
        city_input.clear()
        city_input.send_keys("Scriptville")
        
        state_input.clear()
        state_input.send_keys("PY")
        
        zip_input.clear()
        zip_input.send_keys("12345")
        print("INFO: Shipping address form filled.")
    except (TimeoutException, NoSuchElementException) as e:
        raise Exception(f"FAIL: Could not find or interact with shipping address form fields. Error: {e}")

    # 3. Select Shipping Method
    print("INFO: Selecting 'Express Shipping' method...")
    try:
        # Click the label associated with the express shipping radio button
        express_shipping_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Express Shipping')]")))
        express_shipping_label.click()
        print("INFO: Shipping method selected.")
    except TimeoutException:
        raise Exception("FAIL: Could not find or click the 'Express Shipping' option.")

    # 4. Place the Order
    print("INFO: Placing the order...")
    try:
        place_order_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Place Order']")))
        place_order_button.click()
    except TimeoutException:
        raise Exception("FAIL: Could not find or click the 'Place Order' button.")

    # 5. Verify Order Confirmation
    print("INFO: Verifying order confirmation...")
    try:
        # Check for the success flash message
        success_message_locator = (By.XPATH, "//div[contains(@class, 'flash-success') and contains(text(), 'Order placed successfully!')]")
        wait.until(EC.presence_of_element_located(success_message_locator))
        print("INFO: Success message 'Order placed successfully!' found.")
    except TimeoutException:
        raise Exception("FAIL: Order confirmation message not found after placing order.")

    # 6. Verify Cart is Empty
    print("INFO: Verifying that the cart is now empty...")
    driver.get(f"{BASE_URL}/cart")
    try:
        # Look for the "Your cart is empty" message
        empty_cart_message = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Your cart is empty')]")))
        print("INFO: Cart is confirmed to be empty.")
    except TimeoutException:
        raise Exception("FAIL: Cart was not empty after checkout process.")


if __name__ == "__main__":
    driver = None
    unique_id = uuid.uuid4().hex[:8]
    test_user = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "password123"
    }
    
    try:
        # --- Driver Setup ---
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Uncomment for headless execution
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(2) # Small implicit wait for stability
        except Exception as e:
            print(f"WARN: Selenium Manager failed to start Chrome directly: {e}")
            print("INFO: Falling back to webdriver_manager to install a matching chromedriver.")
            try:
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(2)
            except Exception as e2:
                print(f"ERROR: Failed to start Chrome via webdriver_manager: {e2}")
                raise

        # --- Test Prerequisites ---
        register_and_login(driver, test_user)
        add_item_to_cart(driver)

        # --- Run the Main Test ---
        run_checkout_test(driver)

        # --- Test Result ---
        print("\n-----------------------------------------")
        print("PASS: Full Checkout Process test completed successfully.")
        print("-----------------------------------------")

    except Exception as e:
        print("\n-----------------------------------------")
        print(f"FAIL: An error occurred during the test: {e}")
        print("-----------------------------------------")
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        if driver:
            screenshot_path = f"failure_screenshot_{unique_id}.png"
            driver.save_screenshot(screenshot_path)
            print(f"INFO: Screenshot saved to {screenshot_path}")

    finally:
        if driver:
            driver.quit()
            print("INFO: WebDriver closed.")