from flask import Flask,render_template,request,redirect,url_for,flash,session
from model import db,Product,User,app,Sale

# app = Flask(__name__)
app.config['SECRET_KEY'] = 'DJFKKFI8498'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html',products =products)


@app.route('/sales')
def sales():
    products = Product.query.all()
    sales = Sale.query.all()
    return render_template('sales.html',products= products,sales=sales)


@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        f_name = request.form['f_name']
        email = request.form['email']
        password = request.form['pass']
        user = User.query.filter_by(email=email).all()
        print(user)
        if len(user)< 1:
            new = User (full_name=f_name,email=email,password=password)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("Email already exists",'error')
    return render_template('register.html')


@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).all()
        if len(user) < 1:
            return redirect(url_for('register'))
        else:
            pwd = User.query.filter_by(password=password).all()
            if len(pwd) < 1:
                flash('Incorrect email or password')
            else:
                session['email'] = email
                return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/dashboard')
def dashboard():
    selling = Product.query.filter_by('selling_price').all()
    return render_template('dashboard.html')


@app.route('/add_prods',methods=['GET','POST'])
def add_prods():
    if request.method =='POST':
        name = request.form['name']
        buying = request.form['buying']
        selling = request.form['selling']
        stock_quantity = request.form['stock']
        new = Product(name=name,buying_price=buying,selling_price=selling,stock_quantity=stock_quantity)
        db.session.add(new)
        db.session.commit()
    return redirect(url_for('products'))


@app.route('/make_sale',methods=['GET','POST'])
def make_sale():
    if request.method == 'POST':
        pid = request.form['select_prod']
        quantity = request.form['quantity']
        qun= Sale(product_id = pid,quantity=quantity)
        db.session.add(qun)
        db.session.commit() 
    return redirect(url_for('sales'))


@app.route('/logout')
def log_out():
    session.pop('email',None)
    return redirect(url_for('login'))

app.run(debug=True)