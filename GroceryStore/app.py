from flask import Flask, flash, redirect
from flask import render_template, request, session, url_for
from models import db, User, Admin, Category, Product, Cart, Order
from sqlalchemy import func
from functools import wraps
import os

# --------------------------------------- Application setup ------------------------------------------
app = Flask(__name__, template_folder="templates")
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir,"grocerystore.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "21f3000"

db.init_app(app)
app.app_context().push()

# --------------------------------------- Security decorators -------------------------------------------
#checking if admin is logged in or not
def admin_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'admin_name' and 'admin_id' in session:
            return view_function(*args, **kwargs)
        else:
            flash('Admin login required!!')
            return redirect(url_for('AdminLogin'))
    return decorated_function

#checking if user is logged in or not
def user_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'user_name' and 'user_id' in session:
            return view_function(*args, **kwargs)
        else:
            flash('User login required!!')
            return redirect(url_for('UserLogin'))
    return decorated_function

# --------------------------------------- Home view --------------------------------------------------------
#route to the Home page
@app.route('/')
def Home():
    return render_template('home.html')

# --------------------------------------- Admin controllers ------------------------------------------------
#
@app.route('/admin/signup', methods = ['GET','POST'])
def AdminSign():
    if request.method == 'POST':
        admin = request.form['admin']
        email = request.form['email']
        password = request.form['password']

        admin_check = Admin.query.filter_by(email = email).first()
        if not admin_check:
            new_admin = Admin(admin = admin, 
                        email = email, 
                        password = password)
            
            db.session.add(new_admin)
            db.session.commit()
            admin = Admin.query.filter_by(email = email).first()
            session['admin_name'] = admin.admin
            session['admin_id'] = new_admin.a_id 
            return redirect(url_for('AdminBoard'))
        flash("Admin already exists!")
        return render_template('adminsign.html')
    return render_template('adminsign.html')


@app.route('/admin/login', methods = ['GET','POST'])
def AdminLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin = Admin.query.filter_by(email = email).first()
       
        if admin:
            if (admin.password == password):
                session['admin_name'] = admin.admin
                session['admin_id'] = admin.a_id 
                return redirect(url_for('AdminBoard'))  
            flash("Incorrect password. Please try again!")          
            return render_template("adminlogin.html")
        flash("Admin not found!")
        return render_template('adminlogin.html')
    return render_template('adminlogin.html')


@app.route('/admin/logout')
def AdminOut():
    session.clear()
    return redirect(url_for('AdminLogin'))


@app.route('/addproduct', methods=['GET', 'POST'])
@admin_required
def AddProduct():
    cid = request.args.get('id')
    category_check = Category.query.filter_by(c_id = cid).first()
    if category_check:

        if request.method == 'POST':
            p_name = request.form['product']
            stock = request.form['stock']
            price = request.form['price']
            unit = request.form['unit']


            new_product = Product(c_name = category_check.c_name,
                                c_id = category_check.c_id,
                                p_name = p_name,
                                stock = int(stock),
                                price = int(price),
                                unit = unit)

            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!")
            return redirect(url_for('AdminProducts')) 

        return render_template('addproduct.html', category = category_check, admin = session.get('admin_name'))
    flash("Category doesn't exists!")
    return redirect(url_for('AdminBoard')) 

@app.route('/editproduct', methods=['GET', 'POST'])
@admin_required
def EditProduct():
    pid = request.args.get('id')
    product_check = Product.query.filter_by(p_id = pid).first()
    if product_check:
        if request.method == 'POST':
            p_name = request.form['product']
            unit = request.form['unit']
            price = request.form['price']
            if int(request.form['stock']) >= product_check.stock: 
                product_check.stock = int(request.form['stock'])

            product_check.p_name = p_name
            product_check.unit = unit
            product_check.price = int(price)

            db.session.commit()
            flash("Product updated successfully!")
            return redirect(url_for('AdminProducts')) 
        return render_template('editproduct.html', product = product_check, admin = session.get('admin_name') )
    flash("Product doesn't exists!")
    return redirect(url_for('AdminBoard')) 


@app.route('/deleteproduct')
@admin_required
def DeleteProduct():
    pid = request.args.get('id')
    product_check = Product.query.filter_by(p_id = pid).first()
    if product_check:
        db.session.delete(product_check)
        db.session.commit()
        flash("Product removed successfully!")
        return redirect(url_for('AdminBoard')) 
    flash("Product doesn't exists!")
    return redirect(url_for('AdminBoard')) 


@app.route('/addcategory', methods=['GET', 'POST'])
@admin_required
def AddCategory():
    if request.method == 'POST':
        category = request.form['category']
        category_check = Category.query.filter_by(c_name = category).first()
        if not category_check:
            new_category = Category(c_name = category)
            db.session.add(new_category)
            db.session.commit()
            flash("Category added successfully!")
            return redirect(url_for('AdminBoard')) 
        flash("Category already exists!")
        return render_template('addcategory.html', admin = session.get('admin_name'))
    return render_template('addcategory.html', admin = session.get('admin_name'))


@app.route('/editcategory', methods=['GET', 'POST'])
@admin_required
def EditCategory():
    cid = int(request.args.get('id'))
    category_check = Category.query.filter_by(c_id = cid).first()
    if category_check:
        if request.method == 'POST':
            category = request.form.get('category')
            category_name_check = Category.query.filter_by(c_name = category).first()
            if (category_name_check and category_name_check.c_id == category_check.c_id) or (category_name_check == None):
                category_check.c_name = category
                products = Product.query.filter_by(c_id = category_check.c_id).all()
                for p in products:
                    p.c_name= category
                db.session.commit()
                flash("Category updated successfully!")
                return redirect(url_for('AdminBoard'))
            flash("Category already exists!")
            return render_template('editcategory.html', category = category_check, admin = session.get('admin_name'))
        return render_template('editcategory.html', category = category_check, admin = session.get('admin_name')) 
    flash("Category doesn't exists!")
    return redirect(url_for('AdminBoard')) 


@app.route('/deletecategory')
@admin_required
def DeleteCategory():
    cid = int(request.args.get('id'))
    category_check = Category.query.filter_by(c_id = cid).first()
    if category_check:
        db.session.delete(category_check)
        db.session.commit()
        flash("Category removed successfully!")
        return redirect(url_for('AdminBoard')) 
    flash("Category doesn't exists!")
    return redirect(url_for('AdminBoard')) 


@app.route('/admin/products')
@admin_required
def AdminProducts():
    cid = request.args.get('id')
    if cid:
        products = Product.query.filter_by(c_id = cid).all()
    else:
        products = Product.query.all()
    return render_template('adminproducts.html', products = products, admin = session.get('admin_name'))


@app.route('/admin/dashboard')
@admin_required
def AdminBoard():
    catgories = Category.query.all()
    return render_template('admindashboard.html', catgories = catgories, admin = session.get('admin_name'))


# --------------------------------------- User controllers -------------------------------------------------
@app.route('/user/signup', methods = ['GET', 'POST'])
def UserSign():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user_check = User.query.filter_by(email = email).first()
        if not user_check:
            new_user = User(name = name,
                            email = email,
                            password = password)

            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(email = email).first()
            session['user_name'] = user.name
            session['user_id'] = new_user.u_id
            return redirect(url_for('UserBoard'))
        flash("User already exists!")
        return render_template('usersign.html')
    return render_template('usersign.html')


@app.route('/user/login', methods = ['GET', 'POST'])
def UserLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email = email).first()

        if user:
            if user.password == password:
                session['user_name'] = user.name
                session['user_id'] = user.u_id
                return redirect(url_for('UserBoard'))
            flash("Incorrect password. Please try again!")
            return render_template("userlogin.html")
        flash("User not found!")
        return render_template('userlogin.html')
    return render_template('userlogin.html')


@app.route('/user/logout')
def UserOut():
    session.clear()
    return redirect(url_for('UserLogin'))


@app.route('/user/dashboard')
@user_required
def UserBoard():
    products = Product.query.all()
    return render_template('userdashboard.html', products = products, user = session.get('user_name'))


@app.route('/user/orders')
@user_required
def Orders():
    orders = Order.query.all()
    return render_template('orders.html', orders = orders, user = session.get('user_name'))

@app.route('/view/cart')
@user_required
def ViewCart():
    products = Cart.query.filter_by(u_id = session.get('user_id')).all()
    total = 0
    for p in products:
        total += p.quantity * p.price
    return render_template('cart.html', products = products, total = total, user = session.get('user_name'))


@app.route('/add/cart', methods=['GET', 'POST'])
@user_required
def CartManager():
    pid = request.args.get('id')
    product_check = Product.query.filter_by(p_id = pid).first()
    cart_check = Cart.query.filter_by(p_id = pid).first()
    if not cart_check:
        if request.method == 'POST' and product_check:
            quantity = request.form.get('quantity')
            new_cart = Cart(p_name = product_check.p_name,
                            price = product_check.price,
                            unit = product_check.unit,
                            p_id = product_check.p_id,
                            quantity = int(quantity),
                            u_id = session.get("user_id"))
            db.session.add(new_cart)
            db.session.commit()
            flash("Product is added to cart!")
            return redirect(url_for('UserBoard'))
        return render_template('addtocart.html', product = product_check, user = session.get('user_name'))
    flash("Product already exists in the cart!")
    return redirect(url_for('UserBoard'))


@app.route('/purchase/cart')
@user_required
def PurchaseCart():
    products = Cart.query.filter_by(u_id = session.get('user_id')).all()
    for p in products:
        product_check = Product.query.filter_by(p_id = p.p_id).first()
        if product_check and (product_check.stock - product_check.sold >= p.quantity):
            new_order = Order(o_name = p.p_name,
                            price = p.price,
                            unit = p.unit,
                            p_id = p.p_id,
                            quantity = p.quantity,
                            u_id = session.get("user_id"))
            product_check.sold = product_check.sold + int(p.quantity)
            db.session.add(new_order)
            db.session.delete(p)
    db.session.commit()
    flash("Thankyou for shopping with us!")
    return redirect(url_for('UserBoard'))


@app.route('/user/search')
@user_required
def SearchProduct():
    args = request.args
    query = args.get('q')
    query_string = f'%{query}%'
    results = Product.query.filter(
        (func.lower(Product.p_name).like(query_string)) |
        (func.lower(Product.c_name).like(query_string)) |
        (Product.price == query)).all()
    return render_template("userdashboard.html", products = results, user = session.get('user_name'))


# Run the Flask app
if __name__ == '__main__':
  db.create_all()
  query = Admin.query.all()
  if len(query) == 0:
    admin = Admin(admin = "Admin", email = "admin@gmail.com", password = "1100")
    db.session.add(admin)
    db.session.commit()
  app.run(debug=True)