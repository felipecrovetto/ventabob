from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default='seller')  # 'admin' o 'seller'
    sales = db.relationship('Sale', backref='seller', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sales = db.relationship('Sale', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    quantity = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20)) # 'cash' or 'card'

    def __repr__(self):
        return f'<Sale {self.id} - {self.product.name}>'