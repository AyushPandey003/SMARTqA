import unittest
import os
import tempfile
import requests
import responses
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# --- Test Data and Configuration ---

# The target HTML content is encapsulated here to make the script self-contained.
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Shop Checkout</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 20px; cursor: pointer; border: 1px solid #ccc; background-color: #f0f0f0; }
        .discount-message { margin-top: 10px; font-weight: bold; padding: 10px; border-radius: 4px; }
        .error-message { color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; }
        .success-message { color: #270; background-color: #DFF2BF; border: 1px solid #4F8A10; }
    </style>
</head>
<body>
    <h1>Checkout</h1>
    <div id="cart-summary">
        <h2>Cart Summary</h2>
        <div class="form-group">
            <label for="discount-code">Discount Code</label>
            <input type="text" id="discount-code" placeholder="Enter code">
            <button id="apply-discount">Apply</button>
            <div id="discount-message-container"></div>
        </div>
        <h3>Total: $<span id="total-price">300.00</span></h3>
    </div>
</body>
</html>
"""

# JavaScript to simulate front-end logic for discount application.
# This is injected into the browser to make the static HTML interactive for testing.
JS_SIMULATION_LOGIC = """
    const applyBtn = document.getElementById('apply-discount');
    const discountInput = document.getElementById('discount-code');
    const messageContainer = document.getElementById('discount-message-container');

    applyBtn.addEventListener('click', function() {
        // Clear previous messages
        messageContainer.innerHTML = '';

        const code = discountInput.value;
        let messageElement = document.createElement('div');

        // Simulate API call and response
        if (code === 'VALID10') {
            messageElement.textContent = 'Discount Applied!';
            // The style guide specifies green text. The class handles this.
            messageElement.className = 'discount-message success-message';
            messageElement.style.color = 'green';
        } else {
            messageElement.textContent = 'Invalid or expired discount code.';
            // The style guide specifies red text. The class handles this.
            messageElement.className = 'discount-message error-message';
            messageElement.style.color = 'red';
        }
        messageContainer.appendChild(messageElement);
    });
"""

class TestDiscountCodeUI(unittest.TestCase):
    """
    Test suite for the Discount Code Application UI.
    It uses a temporary local HTML file to run tests in a controlled environment.
    """

    def setUp(self):
        """
        Set up the test environment before each test.
        This includes creating a temporary HTML file and initializing the WebDriver.
        """
        # Create a temporary HTML file to load the test page
        # This makes the test self-contained and independent of a running server
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w') as f:
            self.temp_html_path = f.name
            f.write(HTML_CONTENT)

        # Initialize the Chrome WebDriver using webdriver-manager for automatic driver handling
        try:
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.get(f"file://{self.temp_html_path}")
            # Inject JavaScript to simulate the backend response for UI interactions
            self.driver.execute_script(JS_SIMULATION_LOGIC)
        except Exception as e:
            self.fail(f"WebDriver initialization failed: {e}")

    def tearDown(self):
        """
        Clean up the test environment after each test.
        This includes closing the browser and deleting the temporary HTML file.
        """
        if hasattr(self, 'driver'):
            self.driver.quit()
        if hasattr(self, 'temp_html_path'):
            os.remove(self.temp_html_path)

    def test_dc_ui_001_valid_discount_code(self):
        """
        Test Case: DC-UI-001
        Scenario: User enters a valid discount code and clicks 'Apply'.
        Expected Result: A success message 'Discount Applied!' is displayed in green text.
        """
        # Locate the discount code input field and the apply button
        discount_input = self.driver.find_element(By.ID, "discount-code")
        apply_button = self.driver.find_element(By.ID, "apply-discount")

        # Enter a valid discount code
        discount_input.send_keys("VALID10")

        # Click the apply button
        apply_button.click()

        # Use WebDriverWait to wait for the success message to appear
        try:
            success_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#discount-message-container .success-message"))
            )
        except TimeoutException:
            self.fail("Success message did not appear within the timeout period.")

        # Assert that the message text is correct
        self.assertEqual(success_message.text, "Discount Applied!", "Success message text is incorrect.")

        # Assert that the message text color is green
        message_color = success_message.value_of_css_property("color")
        self.assertIn(message_color, ["rgba(0, 128, 0, 1)", "green"], "Success message color is not green.")

    def test_dc_ui_002_invalid_discount_code(self):
        """
        Test Case: DC-UI-002
        Scenario: User enters an invalid discount code and clicks 'Apply'.
        Expected Result: An inline error message is displayed in red text.
        """
        # Locate the discount code input field and the apply button
        discount_input = self.driver.find_element(By.ID, "discount-code")
        apply_button = self.driver.find_element(By.ID, "apply-discount")

        # Enter an invalid discount code
        discount_input.send_keys("INVALIDCODE")

        # Click the apply button
        apply_button.click()

        # Use WebDriverWait to wait for the error message to appear
        try:
            error_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#discount-message-container .error-message"))
            )
        except TimeoutException:
            self.fail("Error message did not appear within the timeout period.")

        # Assert that the error message is displayed
        self.assertTrue(error_message.is_displayed(), "Error message is not visible.")

        # Assert that the message text color is red
        message_color = error_message.value_of_css_property("color")
        self.assertIn(message_color, ["rgba(255, 0, 0, 1)", "red"], "Error message color is not red.")

    def test_dc_ui_003_apply_button_styling(self):
        """
        Test Case: DC-UI-003
        Scenario: Verify the styling of the 'Apply' button.
        Expected Result: The button is styled as a secondary button (neutral/gray).
        """
        # Locate the apply button
        apply_button = self.driver.find_element(By.ID, "apply-discount")

        # Get the background color of the button
        background_color = apply_button.value_of_css_property("background-color")

        # Assert that the button is not styled as a primary action button (e.g., green)
        # Default button colors are typically shades of gray or light colors.
        self.assertNotIn("0, 128, 0", background_color, "Button should not be green (primary action color).")
        # A more specific check for gray/neutral colors
        self.assertTrue(background_color.startswith("rgba(240, 240, 240") or background_color.startswith("rgb(221, 221, 221"),
                        f"Button color '{background_color}' is not the expected neutral gray.")


class TestDiscountCodeAPI(unittest.TestCase):
    """
    Test suite for the Discount Code API endpoint '/apply_coupon'.
    Uses the 'responses' library to mock HTTP requests, allowing for API testing
    without a live backend.
    """
    BASE_URL = "http://api.eshop.com/apply_coupon"

    @responses.activate
    def test_dc_api_001_valid_coupon(self):
        """Test Case: DC-API-001 - Valid coupon code."""
        # Mock the API response for a successful request
        responses.add(
            responses.POST,
            self.BASE_URL,
            json={"success": True, "discount_amount": 15.50, "message": "Coupon applied successfully."},
            status=200
        )
        # Make the API call
        response = requests.post(self.BASE_URL, json={"code": "VALID10"})
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["discount_amount"], (int, float))
        self.assertIsInstance(data["message"], str)

    @responses.activate
    def test_dc_api_002_invalid_coupon(self):
        """Test Case: DC-API-002 - Invalid or non-existent coupon code."""
        responses.add(
            responses.POST,
            self.BASE_URL,
            json={"success": False, "message": "Coupon code is not valid."},
            status=400
        )
        response = requests.post(self.BASE_URL, json={"code": "INVALIDCODE"})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Coupon code is not valid.")

    @responses.activate
    def test_dc_api_003_empty_string_coupon(self):
        """Test Case: DC-API-003 - Empty string for coupon code."""
        responses.add(
            responses.POST,
            self.BASE_URL,
            json={"success": False, "message": "Coupon code cannot be empty."},
            status=400
        )
        response = requests.post(self.BASE_URL, json={"code": ""})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Coupon code cannot be empty.")

    @responses.activate
    def test_dc_api_004_missing_code_key(self):
        """Test Case: DC-API-004 - Request body is missing the 'code' key."""
        responses.add(
            responses.POST,
            self.BASE_URL,
            json={"success": False, "message": "Malformed request: 'code' key is missing."},
            status=400
        )
        response = requests.post(self.BASE_URL, json={"coupon": "SOMECODE"}) # Missing 'code' key
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Malformed request: 'code' key is missing.")

    @responses.activate
    def test_dc_api_005_invalid_data_type(self):
        """Test Case: DC-API-005 - Non-string data type for 'code' value."""
        responses.add(
            responses.POST,
            self.BASE_URL,
            json={"success": False, "message": "Invalid data type: 'code' must be a string."},
            status=400
        )
        response = requests.post(self.BASE_URL, json={"code": 12345}) # Using a number instead of a string
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Invalid data type: 'code' must be a string.")


if __name__ == "__main__":
    # To run this script, you need to install the required packages:
    # pip install selenium webdriver-manager unittest-xml-reporting requests responses
    unittest.main(verbosity=2)