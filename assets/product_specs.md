# Product Specifications - Ecommerce Test Application

## Products
The store offers the following products:

### T-Shirts
- **Classic White Tee**: $25.00
  - Description: A classic white t-shirt for everyday wear
  - Category: T-Shirts

### Jeans
- **Denim Jeans**: $79.99
  - Description: Classic blue denim jeans with a perfect fit
  - Category: Jeans

### Jackets
- **Leather Jacket**: $149.50
  - Description: Stylish black leather jacket for any occasion
  - Category: Jackets

### Shoes
- **Running Sneakers**: $120.00
  - Description: Comfortable running sneakers with great support
  - Category: Shoes

### Accessories
- **Stylish Sunglasses**: $45.00
  - Description: Modern sunglasses for sunny days
  - Category: Accessories

- **Canvas Backpack**: $60.00
  - Description: Durable canvas backpack for daily use
  - Category: Accessories

## Coupon Codes
The application supports coupon codes for discounts:
- **SAVE20**: Applies a 20% discount to the cart subtotal
  - Applied via the cart page using the "Apply Coupon" button
  - Discount persists through the checkout process
  - Stored in cookies with 1-hour expiration
  - Can be removed using the "Remove Coupon" button
  - Invalid coupon codes display an error message

## Cart & Checkout Logic

### Cart Functionality
- **Add to Cart**: Users can add items to their cart. If an item already exists, its quantity is increased by 1
- **Cart Display**: Shows all cart items with product details, quantities, and individual totals
- **Subtotal Calculation**: Sum of (Item Price × Quantity) for all items
- **Discount Application**: If coupon code is applied, discount = subtotal × 0.20
- **Total Calculation**: Subtotal - Discount
- **Remove Items**: Users can remove individual items from cart

### Checkout Process
- **Authentication Required**: Users must be logged in to access checkout
- **Checkout Page Displays**:
  - 3-step stepper UI (Shipping, Payment, Review)
  - Shipping address form (Full Name, Street Address, City, State, ZIP Code)
  - Shipping method selection:
    - Standard Shipping: $5.00 (4-6 business days) - selected by default
    - Express Shipping: $15.00 (1-2 business days)
  - Order summary with cart items, quantities, subtotal, shipping, and total
- **Order Placement**:
  - Creates an Order record with total_price, discount_amount, and coupon_code
  - Clears all items from the cart
  - Clears the applied coupon code
  - Redirects to home page with success message
  - Order status is set to "Completed"

### Search and Browse
- **Search**: Users can search products by name, category, or description
- **Category Filter**: Filter products by category (T-Shirts, Jeans, Jackets, Shoes, Accessories)
- **Product Detail**: Each product has a dedicated detail page

## User Accounts
- **Registration**: Users register with username, email, and password
  - Passwords are hashed using werkzeug.security
  - Duplicate usernames are rejected
- **Login**: Users login with username and password
  - Failed login attempts show "Invalid username or password"
- **Authentication**: Cart, checkout, profile, and orders require login
- **Profile Page**: Users can view their account information
- **Order History**: Users can view all their past orders with details

## Database Models

### User
- id (Integer, Primary Key)
- username (String, Unique, Required)
- email (String, Unique, Required)
- password_hash (String)
- Relationships: cart_items, orders

### Product
- id (Integer, Primary Key)
- name (String, Required)
- price (Float, Required)
- image_url (String, Required)
- category (String, Default: 'General')
- description (String)

### CartItem
- id (Integer, Primary Key)
- user_id (Foreign Key to User)
- product_id (Foreign Key to Product)
- quantity (Integer, Default: 1)
- Relationship: product

### Order
- id (Integer, Primary Key)
- user_id (Foreign Key to User)
- total_price (Float, Required)
- discount_amount (Float, Default: 0.0)
- coupon_code (String, Nullable)
- status (String, Default: 'Pending')
- created_at (DateTime, Default: UTC now)

## Features Summary
✅ User registration and authentication
✅ Product browsing with search and category filters
✅ Shopping cart with quantity management
✅ **Coupon code functionality (SAVE20 for 20% off)**
✅ Checkout with shipping address and method selection
✅ Order placement and history tracking
✅ User profile management
