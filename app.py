from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Initialize the Listings Database (for storing apartment listings)
def init_listings_db():
    conn = sqlite3.connect('listings.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Insert sample listings into the listings database
def insert_sample_listings():
    listings = [
        ('Studio Apartment', 1400, 'Downtown'),
        ('2-Bedroom Apartment', 1200, 'University Hill'),
        ('3-Bedroom House', 1800, 'Eastside'),
        ('1-Bedroom Apartment', 900, 'Downtown')
    ]
    conn = sqlite3.connect('listings.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO listings (title, price, location) VALUES (?, ?, ?)', listings)
    conn.commit()
    conn.close()

# Initialize the Users Database (for managing user login and sign-up)
def init_users_db():
    conn = sqlite3.connect('users.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home route (Listings page with filter functionality)
@app.route('/')
def home():
    conn = sqlite3.connect('listings.db')
    cursor = conn.cursor()

    # Get filter values from the request
    region = request.args.get('region')
    price = request.args.get('price')

    # Build the SQL query with filters
    query = 'SELECT * FROM listings WHERE 1=1'  # Always true so we can append conditions dynamically
    params = []

    if region:
        query += ' AND location = ?'
        params.append(region)

    if price:
        query += ' AND price <= ?'
        params.append(price)

    cursor.execute(query, params)
    listings = cursor.fetchall()
    conn.close()

    # Prepare listings as a list of dictionaries to send to the template
    listings_data = [{'title': row[1], 'price': row[2], 'location': row[3]} for row in listings]

    return render_template('index.html', listings=listings_data)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # user[2] is the hashed password
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Login failed. Incorrect username or password."

    return render_template('login.html')

# Sign-up route
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash the password before saving it to the database
        hashed_password = generate_password_hash(password, method='sha256')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_password, email))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_listings_db()  # Initialize the listings database (create table if not exists)
    insert_sample_listings()  # Insert sample listings
    init_users_db()  # Initialize the users database (create table if not exists)
    app.run(debug=True)
