from flask import render_template, flash, redirect, url_for, request
from app import app, db
from models import User, Product, CartItem, Order
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query
    
    if search_query:
        query = query.filter(
            (Product.name.ilike(f'%{search_query}%')) | 
            (Product.category.ilike(f'%{search_query}%')) |
            (Product.description.ilike(f'%{search_query}%'))
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()
    return render_template('index.html', products=products, search_query=search_query, category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not check_password_hash(user.password_hash, request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
    db.session.commit()
    flash('Item added to cart')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    items = current_user.cart_items.all()
    subtotal = sum(item.product.price * item.quantity for item in items)
    
    # Get coupon from session
    coupon_code = request.cookies.get('coupon_code', '')
    discount = 0
    if coupon_code == 'SAVE20':
        discount = subtotal * 0.20
    
    total = subtotal - discount
    return render_template('cart.html', items=items, subtotal=subtotal, discount=discount, total=total, coupon_code=coupon_code)

@app.route('/apply_coupon', methods=['POST'])
@login_required
def apply_coupon():
    coupon_code = request.form.get('coupon_code', '').strip().upper()
    
    if coupon_code == 'SAVE20':
        flash('Coupon code applied! 20% discount activated.')
        response = redirect(url_for('cart'))
        response.set_cookie('coupon_code', coupon_code, max_age=3600)
        return response
    else:
        flash('Invalid coupon code')
        return redirect(url_for('cart'))

@app.route('/remove_coupon')
@login_required
def remove_coupon():
    response = redirect(url_for('cart'))
    response.set_cookie('coupon_code', '', max_age=0)
    flash('Coupon code removed')
    return response

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get(item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET'])
@login_required
def checkout_page():
    items = current_user.cart_items.all()
    subtotal = sum(item.product.price * item.quantity for item in items)
    
    # Get coupon from session
    coupon_code = request.cookies.get('coupon_code', '')
    discount = 0
    if coupon_code == 'SAVE20':
        discount = subtotal * 0.20
    
    total = subtotal - discount
    return render_template('checkout.html', items=items, subtotal=subtotal, discount=discount, total=total, coupon_code=coupon_code)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    items = current_user.cart_items.all()
    if not items:
        flash('Cart is empty')
        return redirect(url_for('index'))
    
    subtotal = sum(item.product.price * item.quantity for item in items)
    
    # Get coupon from session
    coupon_code = request.cookies.get('coupon_code', '')
    discount = 0
    if coupon_code == 'SAVE20':
        discount = subtotal * 0.20
    
    total = subtotal - discount
    
    order = Order(
        user_id=current_user.id, 
        total_price=total,
        discount_amount=discount,
        coupon_code=coupon_code if coupon_code else None,
        status='Completed'
    )
    db.session.add(order)
    
    for item in items:
        db.session.delete(item)
    
    db.session.commit()
    
    # Clear coupon after order
    flash('Order placed successfully!')
    response = redirect(url_for('index'))
    response.set_cookie('coupon_code', '', max_age=0)
    return response

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/orders')
@login_required
def orders():
    orders = current_user.orders.all()
    return render_template('orders.html', orders=orders)

def seed_products():
    products = [
  {
    "name": "Classic White Tee",
    "price": 25.00,
    "category": "T-Shirts",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/T-Shirt_Wikipedia_white.jpg",
    "description": "A classic white t-shirt for everyday wear."
  },
  {
    "name": "Denim Jeans",
    "price": 79.99,
    "category": "Jeans",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Blue_jeans_-_detail_06.jpg",
    "description": "Classic blue denim jeans with a perfect fit."
  },
  {
    "name": "Leather Jacket",
    "price": 149.50,
    "category": "Jackets",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Black_worn_leather_jacket.jpg",
    "description": "Stylish black leather jacket for any occasion."
  },
  {
    "name": "Running Sneakers",
    "price": 120.00,
    "category": "Shoes",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Running_shoes_display.JPG",
    "description": "Comfortable running sneakers with great support."
  },
  {
    "name": "Stylish Sunglasses",
    "price": 45.00,
    "category": "Accessories",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Leo_XI_2_Sunglasses.png",
    "description": "Modern sunglasses for sunny days."
  },
  {
    "name": "Canvas Backpack",
    "price": 60.00,
    "category": "Accessories",
    "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Backpack-1.jpg",
    "description": "Durable canvas backpack for daily use."
  }
]
    for p_data in products:
        p = Product(**p_data)
        db.session.add(p)
    db.session.commit()
