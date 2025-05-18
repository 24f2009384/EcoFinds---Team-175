from flask import Flask, render_template, session, redirect, url_for, request, flash
from backend import models
from backend.models import *
import os
from werkzeug.utils import secure_filename
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'team175secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'assets')

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    items = [
            {
                'id': 1,
                'title': 'Maruti Suzuki Alto 800 - 2022',
                'price': '4,50,000',
                'location': 'Jammu',
                'image_url': '/static/assets/alto.png'  # Place image in static/img/
            },
            {
                'id': 2,
                'title': 'iPhone 11 128GB',
                'price': '5,999',
                'location': 'Maharashtra',
                'image_url': '/static/assets/iphone11.png'
            },
            {
                'id': 3,
                'title': 'iPhone 14 Series Sale',
                'price': '19,876',
                'location': 'MIDC Maharashtra',
                'image_url': '/static/assets/iphone14.png'
            },
            {
                'id': 4,
                'title': 'Samsung Galaxy S21',
                'price': '1,999',
                'location': 'Delhi',
                'image_url': '/static/assets/samsung.png'
            },
            {
                'id': 5,
                'title': 'Dell Inspiron 15',
                'price': '45,000',
                'location': 'Mumbai',
                'image_url': '/static/assets/dell.png'
            },
            {
                'id': 6,
                'title': 'HP Pavilion Gaming Laptop',
                'price': '65,000',
                'location': 'Bangalore',
                'image_url': '/static/assets/hp.png'
            }
           ]
    return render_template('index.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        city = request.form['city']
        phone_number = request.form['phone_number']
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.')
            return redirect(url_for('login'))
        file = request.files.get('profile_picture')
        profile_pic_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, 'static', 'assets')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file.save(os.path.join(upload_folder, filename))
            profile_pic_path = f'assets/{filename}'

        new_user = User(
            username=username,
            name=name,
            email=email,
            password=password,
            city=city,
            phone_number=phone_number,
            profile_picture=profile_pic_path  # saved path to DB
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful!')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if User.id in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the user exists
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully.')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password.')    
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove the user from the session
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))   
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    # Get the all the products that others have uploaded too
    products = Product.query.all()

    # Get the user's previous purchases
    previous_purchases = PreviousPurchase.query.filter_by(user_id=user.id).all()
    # Get the user's cart
    cart = Cart.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, products=products, previous_purchases=previous_purchases, cart=cart, )

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.password = request.form['password']
        
        user.city = request.form['city']
        
        user.phone_number = request.form['phone_number']
        user.name = request.form['name']

        # Handle profile picture upload
        file = request.files.get('profile_picture')
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                file.save(save_path)
                user.profile_picture = f'assets/{filename}'
            else:
                flash('Please upload a valid image file.')
                return redirect(request.url)
            
            
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        city = request.form['city']
        user_id = session['user_id']

        file = request.files.get('image_file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Create folder if doesn't exist
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                
            file.save(save_path)

            image_url = f'assets/{filename}'  # path relative to 'static'

        else:
            flash('Please upload a valid image file.')
            return redirect(request.url)

        date_added = datetime.now()

        new_product = Product(
            name=name,
            description=description,
            price=price,
            city=city,
            user_id=user_id,
            image_url=image_url,
            date_added=date_added
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully.')
        return redirect(url_for('profile'))

    return render_template('sell.html')


@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.city = request.form['city']

        file = request.files.get('image_file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            product.image_url = f'assets/{filename}'

        db.session.commit()
        flash('Product updated successfully.')
        return redirect(url_for('profile'))

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    product = Product.query.get_or_404(product_id)
    if product.user_id != session['user_id']:
        flash('You can only delete your own products.')
        return redirect(url_for('profile'))
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.')
    return redirect(url_for('profile'))


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if existing_cart_item:
        flash('Product already in cart.')
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id)
        db.session.add(new_cart_item)
        db.session.commit()
        flash('Product added to cart.')

    return redirect(url_for('profile'))


@app.route('/view_cart')
def view_cart():
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    products = [Product.query.get(item.product_id) for item in cart_items]
    return render_template('cart.html', products=products)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart.')
    else:
        flash('Product not found in cart.')

    return redirect(url_for('view_cart'))


# search functionality
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    products = []

    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()

    return render_template('search_results.html', products=products, query=query)
















if __name__ == '__main__':
    app.run(debug=True)