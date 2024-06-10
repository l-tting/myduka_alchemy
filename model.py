from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

#flask instance
app = Flask(__name__)
#connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:6979@localhost/letting'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initializing sqlalchemy instance
db =SQLAlchemy(app)

#product model
class Product(db.Model):
    __tablename__= 'products'
    id = db.Column(db.Integer,primary_key=True,nullable = False)
    name = db.Column(db.String,nullable=False,unique=True)
    buying_price = db.Column(db.Integer,nullable=False)
    selling_price = db.Column(db.Integer,nullable=False)
    stock_quantity = db.Column(db.Integer,nullable=False)
    #foreign key r/ship
    sales = db.relationship('Sale',backref='product')
    def __repr__(self):
        return f'<PRODUCTS %r> = {self.id} ,name = {self.name}, buying_price = {self.buying_price},selling_price = {self.selling_price},stock_quantity = {self.stock_quantity}'

#sale model
class Sale(db.Model):
    __tablename__= 'sales'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    created_at =db.Column(db.DateTime,nullable=False,default = datetime.utcnow())


#user model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    full_name =db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False,unique=True)
    password=db.Column(db.String,nullable=False)


#accessing current application context
with app.app_context():
    db.create_all()


# app.run(debug=True)