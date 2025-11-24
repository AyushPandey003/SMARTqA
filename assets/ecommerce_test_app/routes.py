from flask import render_template, flash, redirect, url_for, request
from app import app, db
from models import User, Product, CartItem, Order
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

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
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get(item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    items = current_user.cart_items.all()
    if not items:
        flash('Cart is empty')
        return redirect(url_for('index'))
        
    total = sum(item.product.price * item.quantity for item in items)
    order = Order(user_id=current_user.id, total_price=total, status='Completed')
    db.session.add(order)
    
    for item in items:
        db.session.delete(item)
    
    db.session.commit()
    flash('Order placed successfully!')
    return redirect(url_for('index'))

def seed_products():
    products = [
        {"name": "Wireless Headphones", "price": 99.99, "icon": "fa-headphones", "description": "High quality wireless sound."},
        {"name": "Smart Watch", "price": 149.50, "icon": "fa-clock", "description": "Track your fitness and time."},
        {"name": "Mechanical Keyboard", "price": 120.00, "icon": "fa-keyboard", "description": "Clicky and tactile."},
        {"name": "Gaming Mouse", "price": 59.99, "icon": "fa-mouse", "description": "Precision gaming."},
        {"name": "4K Monitor", "price": 299.99, "icon": "fa-desktop", "description": "Crystal clear display."},
        {"name": "USB-C Hub", "price": 35.00, "icon": "fa-usb", "description": "Connect everything."}
    ]
    for p_data in products:
        p = Product(**p_data)
        db.session.add(p)
    db.session.commit()
