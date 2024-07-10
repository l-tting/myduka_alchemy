from flask import Flask,render_template,request,redirect,url_for,flash,session
# from flask_uploads import UploadSet,IMAGES,configure_uploads
from model import db,Product,User,app,Sale,RegisterForm,LoginForm,ResetForm,ChangePasswordForm
from sqlalchemy import func,desc
from flask_mail import Mail,Message
from flask_login import LoginManager,login_required,login_user,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import URLSafeTimedSerializer 

# from werkzeug.utils import secure_filename
# import os
# app = Flask(__name__)
#secret key - flash & sessions & Mail
app.config['SECRET_KEY'] = 'DJFKKFI8498'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])





# serial = Serializer(app.config['SECRET_KEY'],expires_in=60)
# token =serial.dumps({'user_id': current_user.id})


#mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS']= False
app.config['MAIL_USE_SSL']= True
app.config['MAIL_USERNAME'] = 'brianletting01@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'brianletting01@gmail.com'
app.config['MAIL_PASSWORD'] = 'tmlr uehu ftjs pyky'

#mail instance
mail = Mail(app)

def generate_password_reset_token(email):
    return serializer.dumps(email, salt='password-reset-salt')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#home
@app.route('/')
def home():
    return render_template('index.html')

#products
@app.route('/products')
@login_required
def products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('products.html',products =products)

#sales
@app.route('/sales')
@login_required
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
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("Email already exists", 'error')
    return render_template('register.html', form=form)  # Move the form variable here


#login existing user
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
def contact():
    return render_template('contact.html')


#user dashboard
@app.route('/dashboard')
@login_required
def dashboard():

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

    return render_template('dashboard.html', profit_product=profit_product,sm_summ=sm_summ,sal_td=sal_td,p=p,name=name,sale_product=sale_product,day=day,sale_day=sale_day,profit_day=profit_day,pr_mn=pr_mn) 
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
        new = Product(user_id=current_user.id,name=name,buying_price=buying,selling_price=selling,stock_quantity=stock_quantity)
        db.session.add(new)
        db.session.commit()
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

#sending mail
@app.route('/send',methods= ['GET','POST'])
@login_required
def send():
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

def generate_password_reset_token(user_id):
   return serializer.dumps({"user_id": user_id}, salt='password-reset-salt')


def send_mail(to_email, reset_url):
    msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[to_email])
    msg.body = f'Click the link to reset your password: {reset_url}'
    mail.send(msg)

#reset
@app.route('/reset_request',methods=['GET','POST'])
def reset_password_request():
    form = ResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            user = User.query.filter_by(email=email).first()
            if user:
                token = generate_password_reset_token(user.id)
                reset_url = url_for('reset_password', token=token, _external=True)
                send_mail(email, reset_url)
                flash("Reset Request Sent. Check your mail",'success')
            else:
                flash("Email address not found check email or register",'error')
                return redirect(url_for('register'))
    return render_template('reset_request.html',form =form,legend='Reset Password')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    
    data = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    user_id = data['user_id']
    user = User.query.filter_by(id=user_id).first()
    print(user)


    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(user_id=user_id).first()
            print(user)
            if user:
                hashed_password = generate_password_hash(form.password.data)
                user.password = hashed_password
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('login'))
            else:
                print('User not found.', 'error')
                return redirect(url_for('reset_password_request'))

    return render_template('password.html', form=form)




#logging out
@app.route('/logout')
def log_out():
    
    #logging out
    logout_user()
    return redirect(url_for('login'))

app.run(debug=True)