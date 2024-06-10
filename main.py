from flask import Flask,render_template,request,redirect,url_for,flash,session
from model import db,Product,User,app,Sale
from sqlalchemy import func,desc
# app = Flask(__name__)

#secret key - flash & sessions & Mail
app.config['SECRET_KEY'] = 'DJFKKFI8498'

#home
@app.route('/')
def home():
    return render_template('index.html')

#products
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html',products =products)

#sales
@app.route('/sales')
def sales():
    products = Product.query.all()
    sales = Sale.query.all()
    return render_template('sales.html',products= products,sales=sales)

#register new user
@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        f_name = request.form['f_name']
        email = request.form['email']
        password = request.form['pass']
        user = User.query.filter_by(email=email).all()

        if len(user)< 1:
            new = User (full_name=f_name,email=email,password=password)
            session['f_name']=f_name
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("Email already exists",'error')
    return render_template('register.html')

#login existing user
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
                name = db.session.query(
                    User.full_name
                ).filter_by(email=email).all()
                # print(name[0][0])
                session['name'] = name[0][0]
                session['mail'] = email
                
                return redirect(url_for('dashboard'))
    return render_template('login.html')


#get support
@app.route('/contact')
def contact():
    return render_template('contact.html')


#user dashboard
@app.route('/dashboard')
def dashboard():

    #finding profit per product
    profit_per_product = db.session.query(
        Product.name,
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_product')).join(
                     Sale
                 ).group_by(Product.name).all()
    profit_product = []
    name = []
    for i in profit_per_product:
        name.append(i[0])
        profit_product.append(i[1])

    #finding sales per product
    sale_per_product = db.session.query(
        Product.name,
        func.sum((Sale.quantity * Product.selling_price)).label('Sales_Product')
    ).join(Sale).group_by(Product.name).all()
    sale_product = []
    for i in sale_per_product:
        sale_product.append(i[1])

    #finding sales per day
    sales_per_day = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_Day')
    ).join(Product).group_by(func.date(Sale.created_at)).all()
    sale_day =[]
    for i in sales_per_day:
        sale_day.append(i[1])

    #finding profit per day
    profit_per_day = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label("Profit_Day")
    ).join(Product).group_by(func.date(Sale.created_at)).all()
    profit_day = []
    day =[]
    for i in profit_per_day:
        day.append(str(i[0]))
        profit_day.append(i[1])

    profit_today = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_today')
    ).join(Product).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(1).all()
    for profit in profit_today:
        p = profit[1]
 
    sale_today = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_today')
    ).join(Product).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(1).all()
    for i in sale_today:
        sal_td = i[1]

    #sales monthly
    sale_month = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_today')
    ).join(Product).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(30).all()
    s_m =[]

    for i in sale_month:
        s_m.append(i[1])
    sm_summ = sum(s_m)

    #profit monthly
    profit_month = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_month')
    ).join(Product).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(30).all()
    p_m = []
    for i in profit_month:
        p_m.append(i[1])
    pr_mn = sum(p_m)

    return render_template('dashboard.html', profit_product=profit_product, sale_per_product=sale_per_product, sales_per_day=sales_per_day, profit_today=profit_today,p=p,name=name,day= day ,profit_per_day=profit_per_day,sale_day=sale_day,profit_day=profit_day,sale_product= sale_product,sal_td=sal_td,i=i,s_m=s_m,sm_summ=sm_summ,pr_mn=pr_mn)
        

#adding a product
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

#making a sale
@app.route('/make_sale',methods=['GET','POST'])
def make_sale():
    if request.method == 'POST':
        pid = request.form['select_prod']
        quantity = request.form['quantity']
        qun= Sale(product_id = pid,quantity=quantity)
        db.session.add(qun)
        db.session.commit() 
    return redirect(url_for('sales'))

#logging out
@app.route('/logout')
def log_out():
    session.pop('email',None)
    return redirect(url_for('login'))

app.run(debug=True)