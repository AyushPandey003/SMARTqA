import os
import pathlib
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Target HTML content to be tested
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Shop Checkout</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .container {
            display: flex;
            gap: 20px;
        }

        .products,
        .checkout-form {
            flex: 1;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        .product {
            border-bottom: 1px solid #eee;
            padding: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .cart-summary {
            margin-top: 20px;
            border-top: 2px solid #333;
            padding-top: 10px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }

        input[type="text"],
        input[type="email"] {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
        }

        .error {
            color: red;
            font-size: 0.9em;
            display: none;
        }

        .btn {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            border-radius: 3px;
        }

        .btn-add {
            background-color: #007bff;
            color: white;
        }

        .btn-pay {
            background-color: green;
            color: white;
            width: 100%;
            font-size: 1.1em;
        }

        .success-msg {
            color: green;
            font-weight: bold;
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .hidden {
            display: none;
        }
    </style>
</head>

<body>

    <h1>E-Shop Checkout</h1>

    <div class="container">
        <!-- Products Section -->
        <div class="products">
            <h2>Products</h2>
            <div class="product">
                <span>Wireless Headphones ($100)</span>
                <button class="btn btn-add" onclick="addToCart('Wireless Headphones', 100)">Add to Cart</button>
            </div>
            <div class="product">
                <span>Smart Watch ($150)</span>
                <button class="btn btn-add" onclick="addToCart('Smart Watch', 150)">Add to Cart</button>
            </div>
            <div class="product">
                <span>Laptop Stand ($50)</span>
                <button class="btn btn-add" onclick="addToCart('Laptop Stand', 50)">Add to Cart</button>
            </div>

            <div class="cart-summary">
                <h3>Cart Summary</h3>
                <div id="cart-items"></div>
                <p>Subtotal: $<span id="subtotal">0</span></p>

                <div class="form-group">
                    <label for="discount-code">Discount Code</label>
                    <input type="text" id="discount-code" placeholder="Enter code">
                    <button class="btn" onclick="applyDiscount()" style="margin-top: 5px;">Apply</button>
                    <p id="discount-msg" class="error" style="color: blue; display: none;"></p>
                </div>

                <p><strong>Total: $<span id="total">0</span></strong></p>
            </div>
        </div>

        <!-- Checkout Form -->
        <div class="checkout-form">
            <h2>Customer Details</h2>
            <form id="checkout-form" onsubmit="processPayment(event)">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" required>
                    <span class="error" id="name-error">Name is required</span>
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" required>
                    <span class="error" id="email-error">Please enter a valid email</span>
                </div>

                <div class="form-group">
                    <label for="address">Address</label>
                    <input type="text" id="address" required>
                    <span class="error" id="address-error">Address is required</span>
                </div>

                <div class="form-group">
                    <label>Shipping Method</label>
                    <div>
                        <input type="radio" name="shipping" id="shipping-standard" value="standard" checked
                            onchange="updateTotal()">
                        <label for="shipping-standard" style="display:inline;">Standard (Free)</label>
                    </div>
                    <div>
                        <input type="radio" name="shipping" id="shipping-express" value="express"
                            onchange="updateTotal()">
                        <label for="shipping-express" style="display:inline;">Express ($10)</label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Payment Method</label>
                    <div>
                        <input type="radio" name="payment" id="payment-cc" value="cc" checked>
                        <label for="payment-cc" style="display:inline;">Credit Card</label>
                    </div>
                    <div>
                        <input type="radio" name="payment" id="payment-paypal" value="paypal">
                        <label for="payment-paypal" style="display:inline;">PayPal</label>
                    </div>
                </div>

                <button type="submit" class="btn btn-pay" id="pay-btn">Pay Now</button>
            </form>
            <div id="success-message" class="success-msg">Payment Successful!</div>
        </div>
    </div>

    <script>
        let cart = [];
        let discount = 0;

        function addToCart(name, price) {
            const existingItem = cart.find(item => item.name === name);
            if (existingItem) {
                existingItem.qty++;
            } else {
                cart.push({ name, price, qty: 1 });
            }
            renderCart();
        }

        function renderCart() {
            const cartDiv = document.getElementById('cart-items');
            cartDiv.innerHTML = '';
            let subtotal = 0;
            cart.forEach((item, index) => {
                subtotal += item.price * item.qty;
                const div = document.createElement('div');
                div.innerHTML = `
                ${item.name} - $${item.price} x 
                <input type="number" value="${item.qty}" min="1" style="width: 40px;" onchange="updateQty(${index}, this.value)">
            `;
                cartDiv.appendChild(div);
            });
            document.getElementById('subtotal').innerText = subtotal;
            updateTotal();
        }

        function updateQty(index, qty) {
            if (qty < 1) return;
            cart[index].qty = parseInt(qty);
            renderCart();
        }

        function applyDiscount() {
            const code = document.getElementById('discount-code').value;
            const msg = document.getElementById('discount-msg');
            if (code === 'SAVE15') {
                discount = 0.15;
                msg.innerText = "15% Discount Applied!";
                msg.style.display = 'block';
                msg.style.color = 'green';
            } else {
                discount = 0;
                msg.innerText = "Invalid Code";
                msg.style.display = 'block';
                msg.style.color = 'red';
            }
            updateTotal();
        }

        function updateTotal() {
            let subtotal = 0;
            cart.forEach(item => subtotal += item.price * item.qty);

            let shipping = document.getElementById('shipping-express').checked ? 10 : 0;
            let total = subtotal * (1 - discount) + shipping;

            document.getElementById('total').innerText = total.toFixed(2);
        }

        function processPayment(e) {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const address = document.getElementById('address').value;

            let valid = true;

            if (!name) {
                document.getElementById('name-error').style.display = 'block';
                valid = false;
            } else {
                document.getElementById('name-error').style.display = 'none';
            }

            if (!email || !email.includes('@')) {
                document.getElementById('email-error').style.display = 'block';
                valid = false;
            } else {
                document.getElementById('email-error').style.display = 'none';
            }

            if (!address) {
                document.getElementById('address-error').style.display = 'block';
                valid = false;
            } else {
                document.getElementById('address-error').style.display = 'none';
            }

            if (valid) {
                document.getElementById('success-message').style.display = 'block';
                document.getElementById('pay-btn').disabled = true;
            }
        }
    </script>

</body>

</html>
"""

# Define locators for easier maintenance
DISCOUNT_CODE_INPUT = (By.ID, "discount-code")
APPLY_BUTTON = (By.XPATH, "//button[text()='Apply']")
DISCOUNT_MSG = (By.ID, "discount-msg")
SUBTOTAL_SPAN = (By.ID, "subtotal")
TOTAL_SPAN = (By.ID, "total")
ADD_HEADPHONES_BUTTON = (By.XPATH, "//span[contains(text(), 'Wireless Headphones')]/following-sibling::button")
PAGE_HEADER = (By.TAG_NAME, "h1")

def run_tests():
    """Main function to set up the driver and run all test cases."""
    # Create a temporary HTML file to be loaded by the browser
    file_path = os.path.abspath("checkout.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    
    # Get the file URI for cross-platform compatibility
    file_uri = pathlib.Path(file_path).as_uri()

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # --- Test Execution ---
        
        # DC-001: Verify the presence of discount code elements
        print("--- Running Test DC-001: Verify presence of discount code elements ---")
        driver.get(file_uri)
        wait.until(EC.presence_of_element_located(DISCOUNT_CODE_INPUT))
        wait.until(EC.presence_of_element_located(APPLY_BUTTON))
        print("PASS: Discount code input and Apply button are present.")

        # DC-002: Verify interaction happens without a page reload
        print("\n--- Running Test DC-002: Verify interaction without page reload ---")
        header_element = wait.until(EC.presence_of_element_located(PAGE_HEADER))
        driver.find_element(*DISCOUNT_CODE_INPUT).send_keys("TEST")
        driver.find_element(*APPLY_BUTTON).click()
        wait.until(EC.visibility_of_element_located(DISCOUNT_MSG))
        try:
            # Accessing the header element again. If it throws StaleElementReferenceException, the page reloaded.
            header_text = header_element.text
            assert header_text == "E-Shop Checkout"
            print("PASS: Feedback appeared without a full page reload.")
        except StaleElementReferenceException:
            raise AssertionError("Page reloaded after applying discount code.")

        # DC-003: Apply a valid discount code and verify total is reduced
        print("\n--- Running Test DC-003: Apply a valid discount code ---")
        driver.get(file_uri) # Reset state for a clean test
        # Add an item to the cart
        wait.until(EC.element_to_be_clickable(ADD_HEADPHONES_BUTTON)).click()
        # Wait for subtotal and total to update
        wait.until(EC.text_to_be_present_in_element(SUBTOTAL_SPAN, "100"))
        wait.until(EC.text_to_be_present_in_element(TOTAL_SPAN, "100.00"))
        initial_total = float(driver.find_element(*TOTAL_SPAN).text)
        
        # Apply valid discount code
        driver.find_element(*DISCOUNT_CODE_INPUT).send_keys("SAVE15")
        driver.find_element(*APPLY_BUTTON).click()
        
        # Wait for success message and total to update
        wait.until(EC.text_to_be_present_in_element(DISCOUNT_MSG, "15% Discount Applied!"))
        wait.until(EC.text_to_be_present_in_element(TOTAL_SPAN, "85.00"))
        final_total = float(driver.find_element(*TOTAL_SPAN).text)
        
        assert final_total < initial_total, f"Final total {final_total} was not less than initial total {initial_total}"
        assert final_total == 85.00, f"Final total was {final_total}, expected 85.00"
        print("PASS: Valid discount code applied, success message shown, and total was reduced correctly.")

        # DC-004: Verify the styling of the success message
        print("\n--- Running Test DC-004: Verify success message styling ---")
        success_msg_element = driver.find_element(*DISCOUNT_MSG)
        msg_color = success_msg_element.value_of_css_property("color")
        msg_font_weight = success_msg_element.value_of_css_property("font-weight")
        
        assert "green" in msg_color or "rgb(0, 128, 0)" in msg_color, f"Color was {msg_color}, expected green."
        assert msg_font_weight == "700" or msg_font_weight == "bold", f"Font weight was {msg_font_weight}, expected bold/700."
        print(f"PASS: Success message is green (color: {msg_color}) and bold (font-weight: {msg_font_weight}).")

        # DC-005: Attempt to apply an invalid discount code
        print("\n--- Running Test DC-005: Apply an invalid discount code ---")
        driver.get(file_uri) # Reset state
        wait.until(EC.element_to_be_clickable(ADD_HEADPHONES_BUTTON)).click()
        wait.until(EC.text_to_be_present_in_element(TOTAL_SPAN, "100.00"))
        initial_total = float(driver.find_element(*TOTAL_SPAN).text)

        # Apply invalid code
        driver.find_element(*DISCOUNT_CODE_INPUT).send_keys("INVALIDCODE")
        driver.find_element(*APPLY_BUTTON).click()

        # Wait for error message
        wait.until(EC.text_to_be_present_in_element(DISCOUNT_MSG, "Invalid Code"))
        final_total = float(driver.find_element(*TOTAL_SPAN).text)

        assert initial_total == final_total, f"Total changed from {initial_total} to {final_total}."
        print("PASS: Invalid code showed an error message and the total remained unchanged.")

        # DC-006: Verify the styling of the error message
        print("\n--- Running Test DC-006: Verify error message styling ---")
        error_msg_element = driver.find_element(*DISCOUNT_MSG)
        msg_color = error_msg_element.value_of_css_property("color")
        
        assert "red" in msg_color or "rgb(255, 0, 0)" in msg_color, f"Color was {msg_color}, expected red."
        print(f"PASS: Error message is red (color: {msg_color}).")

        # DC-007: Click 'Apply' with an empty discount code field
        print("\n--- Running Test DC-007: Apply with empty field ---")
        driver.get(file_uri) # Reset state
        wait.until(EC.element_to_be_clickable(ADD_HEADPHONES_BUTTON)).click()
        wait.until(EC.text_to_be_present_in_element(TOTAL_SPAN, "100.00"))
        initial_total = float(driver.find_element(*TOTAL_SPAN).text)

        # Clear the input field and click apply
        discount_input = driver.find_element(*DISCOUNT_CODE_INPUT)
        discount_input.clear()
        driver.find_element(*APPLY_BUTTON).click()

        # Wait for error message. The provided JS shows "Invalid Code" for an empty field.
        wait.until(EC.text_to_be_present_in_element(DISCOUNT_MSG, "Invalid Code"))
        final_total = float(driver.find_element(*TOTAL_SPAN).text)

        assert initial_total == final_total, f"Total changed from {initial_total} to {final_total} on empty apply."
        print("PASS: Applying with an empty field showed an error and the total remained unchanged.")

    except TimeoutException as e:
        print(f"\nFAIL: A timeout occurred. Element not found or condition not met in time. {e}")
    except AssertionError as e:
        print(f"\nFAIL: An assertion failed. {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Clean up: close the browser and delete the temporary file
        if 'driver' in locals() and driver:
            driver.quit()
        if os.path.exists(file_path):
            os.remove(file_path)
        print("\n--- Test execution finished. ---")


if __name__ == "__main__":
    run_tests()
