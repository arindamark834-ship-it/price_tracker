import sqlite3

def init_db():
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor()
    # Create products table with a username column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            target_price_selector TEXT NOT NULL
        )
    ''')
    # Create price history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_product(username, title, url, selector):
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO products (username, title, url, target_price_selector) VALUES (?, ?, ?, ?)',
        (username, title, url, selector)
    )
    conn.commit()
    conn.close()

def get_user_products(username):
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url, target_price_selector FROM products WHERE username = ?', (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows