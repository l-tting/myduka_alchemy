from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:6979@localhost/letting'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db =SQLAlchemy(app)

class Product(db.Model):
    __tablename__= 'products'
    id = db.Column(db.Integer,primary_key=True,nullable = False)
    name = db.Column(db.String,nullable=False,unique=True)
    buying_price = db.Column(db.Integer,nullable=False)
    selling_price = db.Column(db.Integer,nullable=False)
    stock_quantity = db.Column(db.Integer,nullable=False)
    sales = db.relationship('Sale',backref='product')

class Sale(db.Model):
    __tablename__= 'sales'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    created_at =db.Column(db.DateTime,nullable=False,default = datetime.utcnow())

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    full_name =db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False,unique=True)
    password=db.Column(db.String,nullable=False)



with app.app_context():
    db.create_all()
app.run(debug=True)