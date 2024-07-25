from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField
from wtforms.validators import Length,InputRequired,ValidationError,DataRequired,EqualTo
from flask_wtf.csrf import CSRFProtect


#flask instance
app = Flask(__name__)
csrf = CSRFProtect(app)

#connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:6979@localhost/shop_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initializing sqlalchemy instance
db =SQLAlchemy(app)
#Bcrypt instance

#product model
class Product(db.Model):
    __tablename__= 'products'
    id = db.Column(db.Integer,primary_key=True,nullable = False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    name = db.Column(db.String,nullable=False)
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
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

#user model
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,nullable=False,unique=True)
    full_name =db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False,unique=True)
    password=db.Column(db.String,nullable=False)
    products = db.relationship('Product',backref='product',lazy=True)

class RegisterForm(FlaskForm):
    full_name = StringField(validators=[InputRequired(),Length(min=4,max=30)],render_kw={'placeholder':'Full Name'})
    email = StringField(validators=[InputRequired(),Length(min=4,max=30)],render_kw={'placeholder':'Email'})
    password = PasswordField(validators=[InputRequired(),Length(min=4,max=100)],render_kw={'placeholder':'Password'})
    submit = SubmitField('Register')
    # def validate_email(self,email):
    #     existing_user = User.query.filter_by(email=email.data).first()
    #     if existing_user:
    #         raise ValidationError("User already exists. Please login")
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    def __init__(self, url):
        self.url = url

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(),Length(min=4,max=30)],render_kw={'placeholder':'Email'})
    password = PasswordField(validators=[InputRequired(),Length(min=4,max=100)],render_kw={'placeholder':'Password'})
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    email = StringField(validators=[InputRequired(),Length(min=4,max=30)],render_kw={'placeholder':'Email'})
    submit = SubmitField("Confirm")

class ChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)],render_kw={'placeholder':'Password'})
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')],render_kw={'placeholder':'Confirm Password'})
    submit = SubmitField('Change Password')

class UpdateProdForm(FlaskForm):
    buying_price = IntegerField(validators=[InputRequired(),Length(min=1)],render_kw={'placeholder':'Buying Price'})
    selling_price = IntegerField(validators=[InputRequired(),Length(min=1)],render_kw={'placeholder':'Buying Price'})
    quantity = IntegerField(validators=[InputRequired(),Length(min=1)],render_kw={'placeholder':'Buying Price'})

class RemoveProdForm(FlaskForm):
    pass

#accessing current application context
with app.app_context():
    db.create_all()


# app.run(debug=True)