from flask  import  Flask,render_template,redirect,url_for,request,session,flash
from model import get_data,insert_products,insert_sales,check_email_exists,insert_user,check_email_password,update_products,profit_per_day,profit_per_product,sales_per_day,sales_per_prod,profit_only,sales_only,check_quantity
from flask_mail import Mail,Message

#app instance
app =  Flask(__name__)

#secret key for flash,sessions,Mail
app.secret_key ='fjfkfifii4848v'

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


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    if 'email' not in session:
        return redirect(url_for('login'))
    products = get_data('products')
    return render_template('products.html',products=products)


@app.route('/sales')
def sales():
    if 'email' not in session:
        return redirect(url_for('login'))
    sales = get_data('sales')
    products = get_data('products')
    return render_template('sales.html',sales = sales,products=products)


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        f_name = request.form['f_name']
        email = request.form['email']
        password = request.form['pass']
        #check if email exists
        check_email =check_email_exists(email)
        #INSERT NEW USER
        if check_email == None:
            new = (f_name,email,password)
            insert_user(new)
            return redirect(url_for('login'))
        else:
            flash('Email exists')
    return render_template('register.html')


@app.route('/contact')
def contact():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')
 

@app.route('/send',methods = ['GET','POST'])
def send():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']
        msg = Message(subject,sender=email,recipients=['brianletting01@gmail.com'])
        msg.body = f'From: {email}\n My name is {name}\n My contact no is {phone}\n\n{message}'
        try:
            mail.send(msg)
            flash('Email sent successfully!','success')
        except Exception as e:
            flash(f'Failed to send email. Error: {str(e)}')
        return redirect(url_for('contact'))



@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    profit_product=profit_per_product()
    profit_day = profit_per_day()
    sales_product = sales_per_prod()
    sales_day = sales_per_day()
    sale_only  = sales_only()
    prof_only = profit_only()
    name = []
    prof_prod = []
    sales_prod =[]
    day_prof = []
    prof_day=[]
    sal_d = []
    sale_on = []
    prf_on = []

    for i in profit_product:
        name.append(i[0])
        prof_prod.append(i[1])
    
    for i in profit_day:
        day_prof.append(str(i[0]))
        prof_day.append(i[1])

    for i in sales_product:
        sales_prod.append(i[1])

    for i in sales_day:
        sal_d.append(float(i[1]))

    for i in sale_only:
        sale_on.append(i)
    for i in prof_only:
        prf_on.append(i)
    return render_template('dashboard.html',name=name, prof_prod=prof_prod, day_prof=day_prof, prof_day=prof_day, sales_prod=sales_prod, sal_d=sal_d,sale_on=sale_on,prf_on=prf_on)


@app.route('/subscribe',methods = ['GET','POST'])  
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        msg = Message(sender=email,recipients=['brianletting01@gmail.com'])
        msg.body = f'From: {email}\n\n User with email- {email} would like to subscribe to MyShop newsletter.'
        try:
            mail.send(msg)
            flash("You've successfully subscribed to our monthly newsletter",'success')
        except Exception as e:
            flash(f'Failed to send email. Error: {str(e)}','error')
        return redirect(url_for('contact'))


@app.route('/login',methods = ['GET','POST'])
def login():
    #GET FORM DATA
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        #CHECK EMAIL EXISTS
        check = check_email_exists(email)
        if check == None:
            return redirect(url_for('register'))
        else:
            #CROSSCHECK PASSWORD AGAINST EMAIL
            ch = check_email_password(email,password)
            if len(ch) < 1:
                flash('Incorrect email or password')
            else:
                #STORE EMAIL IN A SESSION
                session['email']= email
                return redirect(url_for('dashboard'))     
    return render_template('login.html')


@app.route('/add_prods', methods=['GET','POST'] )
def add_prods():
    p_name = request.form['name']
    b_price = request.form['buying']
    s_price = request.form['selling']
    stock = request.form['stock']
    new = (p_name,b_price,s_price,stock)
    insert_products(new)
    return redirect(url_for('products'))


@app.route('/update_prods',methods=['GET','POST'])
def update_prods():
    pid = request.form['select']
    buying = request.form['buying']
    selling = request.form['selling']
    stock = request.form['stock']
    new = (buying,selling,stock)
    update_products(new,pid)
    return redirect(url_for('products'))


@app.route('/make_sale',methods=['GET','POST'])
def make_sale():
    pid = request.form['select']
    quantity = request.form['quantity']
    c_q=check_quantity(pid)
    if c_q>quantity:
        new = (pid,quantity)
        insert_sales(new)
        flash('Sale made successfully')
        
    return redirect(url_for('sales'))


@app.route('/logout')
def log_out():
    session.pop('email',None)
    return redirect(url_for('login'))


app.run(debug=True)