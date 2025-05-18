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
                'title': 'Maruti Suzuki Alto 800 - 2022',
                'price': '4,50,000',
                'location': 'Jammu',
                'image_url': '/static/assests/alto.png'  # Place image in static/img/
            },
            {
                'title': 'iPhone 11 128GB',
                'price': '5,999',
                'location': 'Maharashtra',
                'image_url': '/static/assests/iphone11.png'
            },
            {
                'title': 'iPhone 14 Series Sale',
                'price': '19,876',
                'location': 'MIDC Maharashtra',
                'image_url': '/static/assests/iphone14.png'
            },
            {
                'title': 'Samsung Galaxy S21',
                'price': '1,999',
                'location': 'Delhi',
                'image_url': '/static/assests/samsung.png'
            },
            {
                'title': 'Dell Inspiron 15',
                'price': '45,000',
                'location': 'Mumbai',
                'image_url': '/static/assests/dell.png'
            },
            {
                'title': 'HP Pavilion Gaming Laptop',
                'price': '65,000',
                'location': 'Bangalore',
                'image_url': '/static/assests/hp.png'
            }
           ]
    return render_template('index.html', items = items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        city = request.form['city']
        phone_number = request.form['phone_number']
        name = request.form['name']
        # set profile picture
        profile_picture = request.form['profile_picture']
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in.')
            return redirect(url_for('login'))
        
        # Create a new user
        new_user = User(username=username, email=email, password=password, city=city, phone_number=phone_number, name=name, profile_picture=profile_picture)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully. Please log in.')
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










if __name__ == '__main__':
    app.run(debug=True)