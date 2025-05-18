from flask import Flask, render_template, session, redirect, url_for, request, flash
from backend import models
from backend.models import *
app = Flask(__name__)
app.secret_key = 'team175secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup')
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        profile_picture = request.form['profile_picture']
        city = request.form['city']
        phone_number = request.form['phone_number']
        name = request.form['name']
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in.')
            return redirect(url_for('login'))
        
        # Create a new user
        new_user = User(username=username, email=email, password=password, profile_picture=profile_picture, city=city, phone_number=phone_number, name=name)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully. Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login')
def login():
    # Check if the user is already logged in
    if User.id in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the user exists
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')    
        
    return render_template('login.html')





if __name__ == '__main__':
    app.run(debug=True)