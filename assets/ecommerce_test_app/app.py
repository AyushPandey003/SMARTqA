from flask import Flask
from config import Config
from models import db, User, Product
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed data if empty
        if not Product.query.first():
            from routes import seed_products
            seed_products()
    app.run(debug=True)
