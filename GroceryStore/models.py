from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    name =  db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    carts = relationship('Cart', backref='user', lazy=True)
    orders = relationship('Order', backref='user', lazy=True)

class Admin(db.Model):
    a_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    admin = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(10), nullable=False)

class Category(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(50), unique=True, nullable=False)
    products = relationship('Product', backref='category', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String, nullable=False)
    c_name = db.Column(db.String(50), nullable=False)
    c_id = db.Column(db.Integer, db.ForeignKey('category.c_id'), nullable=False)
    carts = relationship('Cart', backref='product', lazy=True, cascade="all, delete-orphan")    

class Cart(db.Model):
    cr_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String, nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('product.p_id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)

class Order(db.Model):
    o_id = db.Column(db.Integer, primary_key=True)
    o_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String, nullable=False)
    date = db.Column(db.String(16), default=date.today().strftime('%d-%m-%Y'))
    p_id = db.Column(db.Integer, db.ForeignKey('product.p_id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)