import sqlite3

def init_db():
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0.0,
        is_admin BOOLEAN DEFAULT FALSE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        mileage INTEGER NOT NULL,
        description TEXT,
        reserve_price REAL NOT NULL,
        end_time TEXT NOT NULL,
        seller_id INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        time TEXT NOT NULL,
        bidder_id INTEGER NOT NULL,
        vehicle_id INTEGER NOT NULL,
        FOREIGN KEY (bidder_id) REFERENCES users(id),
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        time TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (username, password, email, is_admin)
        VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin123', 'admin@auction.com', True))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
