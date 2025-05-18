# creation of the models for the database using SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    name = db.Column(db.String(80), nullable=True)


    def __repr__(self):
        return f'<User {self.username}>'
    
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_bought = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    
    # relationships
    user = db.relationship('User', backref=db.backref('products', lazy=True))
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
class PreviousPurchase(db.Model):
    __tablename__ = 'previous_purchases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('previous_purchases', lazy=True))
    product = db.relationship('Product', backref=db.backref('previous_purchases', lazy=True))
    
    def __repr__(self):
        return f'<PreviousPurchase {self.user.username} - {self.product.name}>'
    
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('carts', lazy=True))
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))
    
    def __repr__(self):
        return f'<Cart {self.user.username} - {self.product.name}>'