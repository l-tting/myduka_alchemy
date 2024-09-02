from flask import Flask,render_template,request,redirect,url_for,flash,session,make_response
# from flask_uploads import UploadSet,IMAGES,configure_uploads
from model import db,Product,User,app,Sale,RegisterForm,LoginForm,ResetForm,ChangePasswordForm,OTPForm
from sqlalchemy import func,desc
from flask_mail import Mail,Message
from flask_login import LoginManager,login_required,login_user,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import URLSafeTimedSerializer 
import random
from flask_redis import FlaskRedis
from datetime import timedelta
from functools import wraps
#secret key - flash & sessions & Mail
app.config['SECRET_KEY'] = 'DJFKKFI8498'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

#redis
app.config['REDIS_URL'] ='redis://localhost:6379/0'
redis_client = FlaskRedis(app)

#mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS']= False
app.config['MAIL_USE_SSL']= True
app.config['MAIL_USERNAME'] = 'brianletting01@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'brianletting01@gmail.com'
app.config['MAIL_PASSWORD'] = 'ryzk znyx ihig jvwi'

#mail instance
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#no cache
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

#home
@app.route('/')
def home():
    return render_template('index.html')


#products
@app.route('/products')
@login_required
@nocache
def products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('products.html',products =products)

#sales
@app.route('/sales')
@login_required
@nocache
def sales():
    products = Product.query.filter_by(user_id=current_user.id)
    sales = Sale.query.filter_by(user_id=current_user.id).all()
    return render_template('sales.html',products= products,sales=sales)

#register new user
@app.route('/register',methods = ['GET','POST'])
def register():
    form = RegisterForm()  # Define the form outside the if block
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash("User already exists.Please Login",'error')
            else:
                hashed_password = generate_password_hash(form.password.data)
                new_user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('dashboard'))
       
    return render_template('register.html', form=form)  



@app.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if check_password_hash(user.password,form.password.data):
                    login_user(user)
                    session['name'] =  user.full_name
                    session['email'] = user.email
                    flash('Login successful','success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Wrong password','error')
            else:
                flash('User does not exist','error')
        return redirect(url_for('dashboard'))            
    return render_template('login.html',form=form)


#get support
@app.route('/contact')
@login_required
@nocache
def contact():
    return render_template('contact.html')


#user dashboard
@app.route('/dashboard')
@login_required
@nocache

def dashboard():
    product = Product.query.filter_by(user_id=current_user.id).all()
    #finding profit per product
    profit_per_product = db.session.query(
        Product.name,
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_product')).join(
                     Sale
                 ).group_by(Product.name).filter_by(user_id=current_user.id)
    profit_product = []
    name = []
    for i in profit_per_product:
        name.append(i[0])
        profit_product.append(i[1])

    #finding sales per product
    sale_per_product = db.session.query(
        Product.name,
        func.sum((Sale.quantity * Product.selling_price)).label('Sales_Product')
    ).join(Sale).group_by(Product.name).filter_by(user_id=current_user.id)
    sale_product = []
    for i in sale_per_product:
        sale_product.append(i[1])

    #finding sales per day
    sales_per_day = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_Day')
    ).join(Product).group_by(func.date(Sale.created_at)).filter_by(user_id=current_user.id)
    sale_day =[]
    for i in sales_per_day:
        sale_day.append(i[1])

    #finding profit per day
    profit_per_day = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label("Profit_Day")
    ).join(Product).group_by(func.date(Sale.created_at)).filter_by(user_id=current_user.id)
    profit_day = []
    day =[]
    for i in profit_per_day:
        day.append(str(i[0]))
        profit_day.append(i[1])
    p = 0
    profit_today = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_today')
    ).join(Product).filter_by(user_id=current_user.id).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(1).all()
    for profit in profit_today:
        p = profit[1]

    sal_td = 0
    sale_today = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_today')
    ).join(Product).filter_by(user_id=current_user.id).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(1).all()
    for i in sale_today:
        sal_td = i[1]

    #sales monthly
    sale_month = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum(Sale.quantity * Product.selling_price).label('Sales_today')
    ).join(Product).filter_by(user_id=current_user.id).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(30).all()
    s_m =[]

    for i in sale_month:
        s_m.append(i[1])
    sm_summ = sum(s_m)

    #profit monthly
    profit_month = db.session.query(
        func.date(Sale.created_at).label('Date'),
        func.sum((Sale.quantity * Product.selling_price)-
                 (Sale.quantity * Product.buying_price)).label('Profit_month')
    ).join(Product).filter_by(user_id=current_user.id).group_by('Date').order_by(func.date(Sale.created_at).desc()).limit(30).all()
    p_m = []
    for i in profit_month:
        p_m.append(i[1])
    pr_mn = sum(p_m)

    return render_template('dashboard.html', profit_product=profit_product,sm_summ=sm_summ,sal_td=sal_td,p=p,name=name,sale_product=sale_product,day=day,sale_day=sale_day,profit_day=profit_day,pr_mn=pr_mn,product=product) 
# sale_per_product=sale_per_product, sales_per_day=sales_per_day, profit_today=profit_today,p=p,name=name,day= day ,profit_per_day=profit_per_day,sale_day=sale_day,profit_day=profit_day,sale_product= sale_product,sal_td=sal_td,i=i,s_m=s_m,sm_summ=sm_summ,pr_mn=pr_mn)
        

#adding a product
@app.route('/add_prods',methods=['GET','POST'])
@login_required
def add_prods():
    if request.method =='POST':
        name = request.form['name']
        buying = request.form['buying']
        selling = request.form['selling']
        stock_quantity = request.form['stock']
        existing_product = Product.query.filter_by(user_id= current_user.id,name=name).first()
        if existing_product:
            flash("Product already exists")
            return redirect(url_for('products'))
        else:
            new = Product(user_id=current_user.id,name=name,buying_price=buying,selling_price=selling,stock_quantity=stock_quantity)
            db.session.add(new)
            db.session.commit()
    return redirect(url_for('products'))

@app.route('/update_prods',methods=['GET','POST'])
def update_prods():
    name = request.form['select']
    buying = request.form['buying']
    selling = request.form['selling']
    quantity = request.form['stock']
    products = Product.query.filter_by(user_id= current_user.id)
    updated = Product(user_id = current_user.id,name=name,buying_price=buying,selling_price=selling,stock_quantity=quantity)
    db.session.add(updated)
    
    db.session.commit()
    products.stock_quantity += quantity
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/delete_product',methods= ['GET','POST'])
def delete_product():
    if request.method == 'POST':
        name = request.form['product']
        print(name)
        if name:
            product = Product.query.filter_by(user_id=current_user.id, name=name).first()
            if product: 
                db.session.delete(product)
                db.session.commit()
            else:
                flash("Product not found",'error')
        else:
            flash("Product name not provided","error")
    return redirect(url_for('products'))

#making a sale
@app.route('/make_sale',methods=['GET','POST'])
@login_required
def make_sale():
    if request.method == 'POST':
        pid = request.form['select_prod']
        quantity = int(request.form['quantity'])
        product = Product.query.get(pid)
        if product:
            if product.stock_quantity >= quantity:
                sale= Sale( product_id = pid,quantity=quantity,user_id=current_user.id)
                db.session.add(sale)
                db.session.commit() 
                product.stock_quantity -= quantity
                db.session.commit()
                flash(f'Sale of {quantity} units of {product.name} successful!', 'success')
            else:
                flash('Insufficient stock to make sale','error')
        else:
            flash('Product not found','error')
    return redirect(url_for('sales'))


@app.route('/send_support_mail',methods= ['GET','POST'])
@login_required
def send_support_mail():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']
        try:
            msg = Message(subject,sender=email,recipients=['brianletting01@gmail.com'])
            msg.body = f'From: {email}. \n My name is {name}\n My phone no:{phone}\n\n {message}'
            mail.send(msg)
            flash('Email sent successfully!','success')
        except Exception as e:
            flash(f'Failed to send email. Error: {str(e)}')
    return redirect(url_for('contact'))

def generate_otp():
    return random.randint(100000,999999)


@app.route('/reset_request',methods= ['GET','POST'])
def reset_request():
    form = ResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            user = db.session.query(User).filter(User.email==email).first()
            if not user:
                flash("User not found","error")
            else:
                otp = generate_otp()
                redis_key = f'otp:{user.id}'
                redis_client.setex(redis_key, timedelta(minutes=10), otp)
                redis_client.setex(f'{redis_key}_expiration', timedelta(minutes=10), 'valid')
                message = Message(f'From {email}', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
                message.body =  f'Your password reset OTP Code is {otp}'
            try: 
                mail.send(message)
                flash("OTP sent successfully","success")
                session['reset_user_id'] = user.id
                return redirect(url_for('verify_otp'))
            except Exception as e:
                flash(f"Error sending mail ,{e}","error")
    return render_template('reset_request.html',form=form)

@app.route('/otpverification',methods=['GET','POST'])
def verify_otp():
    form= OTPForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            otp = form.otp.data
            user_id = session.get('reset_user_id')
            redis_key = f'otp:{user_id}'
            stored_otp = redis_client.get(redis_key)   
            if stored_otp:
                if str(otp) == stored_otp.decode('utf-8'):
                    flash("OTP verified. Change Password.", "success")
                    redis_client.delete(redis_key)
                    redis_client.delete(f'{redis_key}_expiration')
                    return redirect(url_for('password_reset'))
                else:
                    flash("Invalid otp","error")
            else:
                flash("Invalid OTP or OTP has expired, request new OTP","error")           
    return render_template("otp.html",form=form)
 
@app.route('/passwordreset',methods=['GET','POST'])
def password_reset():
    form = ChangePasswordForm()
    if request.method == 'POST':
         if form.validate_on_submit():
            password = form.password.data
            confirm_password = form.confirm_password.data
            if password == confirm_password:
                hashed_password = generate_password_hash(password)
                user_id = session.get('reset_user_id')
                user = db.session.query(User).filter(User.id==user_id).first()
                if user:
                    user.password = hashed_password
                    db.session.commit()
                    flash("Password changed successfully")
                    return redirect(url_for('login'))
            else:
                flash("Passwords don't match","error")
    return render_template("password_reset.html",form=form)


@app.route('/uploadimg')
def upload_image():
    return render_template()

@app.route('/prof')
def profile():
    return render_template('profile.html')


@app.route('/logout')
def log_out():
    logout_user()
    session.clear()
    flash("You've been logged out successfully","success")
    return redirect(url_for('login'))

app.run(debug=True)