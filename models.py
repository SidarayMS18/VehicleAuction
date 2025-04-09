# models.py
import sqlite3

class User:
    def __init__(self, id=None, username=None, password=None, email=None, balance=0.0, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.balance = balance
        self.is_admin = bool(is_admin)
    
    @classmethod
    def find_by_username(cls, username):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return cls(*user_data)
        return None
    
    def save(self):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        if self.id:
            cursor.execute('''
            UPDATE users SET username=?, password=?, email=?, balance=?, is_admin=?
            WHERE id=?
            ''', (self.username, self.password, self.email, self.balance, self.is_admin, self.id))
        else:
            cursor.execute('''
            INSERT INTO users (username, password, email, balance, is_admin)
            VALUES (?, ?, ?, ?, ?)
            ''', (self.username, self.password, self.email, self.balance, self.is_admin))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

class Vehicle:
    def __init__(self, id=None, make=None, model=None, year=None, mileage=None, 
                 description=None, reserve_price=None, end_time=None, seller_id=None):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.description = description
        self.reserve_price = reserve_price
        self.end_time = end_time
        self.seller_id = seller_id
    
    @classmethod
    def get_all_active(cls):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM vehicles WHERE datetime(end_time) > datetime('now')
        ''')
        vehicles = [cls(*row) for row in cursor.fetchall()]
        conn.close()
        return vehicles
    
    @classmethod
    def get_by_id(cls, vehicle_id):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,))
        vehicle_data = cursor.fetchone()
        conn.close()
        if vehicle_data:
            return cls(*vehicle_data)
        return None
    
    def save(self):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        if self.id:
            cursor.execute('''
            UPDATE vehicles SET make=?, model=?, year=?, mileage=?, description=?, 
            reserve_price=?, end_time=?, seller_id=? WHERE id=?
            ''', (self.make, self.model, self.year, self.mileage, self.description, 
                 self.reserve_price, self.end_time, self.seller_id, self.id))
        else:
            cursor.execute('''
            INSERT INTO vehicles (make, model, year, mileage, description, 
            reserve_price, end_time, seller_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.make, self.model, self.year, self.mileage, self.description,
                 self.reserve_price, self.end_time, self.seller_id))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

class Bid:
    def __init__(self, id=None, amount=None, time=None, bidder_id=None, vehicle_id=None):
        self.id = id
        self.amount = amount
        self.time = time
        self.bidder_id = bidder_id
        self.vehicle_id = vehicle_id
    
    @classmethod
    def get_highest_for_vehicle(cls, vehicle_id):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM bids WHERE vehicle_id=? ORDER BY amount DESC LIMIT 1
        ''', (vehicle_id,))
        bid_data = cursor.fetchone()
        conn.close()
        if bid_data:
            return cls(*bid_data)
        return None
    
    @classmethod
    def get_for_user(cls, user_id):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bids WHERE bidder_id=?', (user_id,))
        bids = [cls(*row) for row in cursor.fetchall()]
        conn.close()
        return bids
    
    def save(self):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO bids (amount, time, bidder_id, vehicle_id)
        VALUES (?, ?, ?, ?)
        ''', (self.amount, self.time, self.bidder_id, self.vehicle_id))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

class Notification:
    def __init__(self, id=None, user_id=None, message=None, time=None, is_read=False):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.time = time
        self.is_read = bool(is_read)
    
    @classmethod
    def get_for_user(cls, user_id, unread_only=False):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        query = 'SELECT * FROM notifications WHERE user_id=?'
        params = [user_id]
        if unread_only:
            query += ' AND is_read=FALSE'
        cursor.execute(query, params)
        notifications = [cls(*row) for row in cursor.fetchall()]
        conn.close()
        return notifications
    
    def mark_as_read(self):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET is_read=TRUE WHERE id=?', (self.id,))
        conn.commit()
        conn.close()
        self.is_read = True
    
    def save(self):
        conn = sqlite3.connect('auction.db')
        cursor = conn.cursor()
        if self.id:
            cursor.execute('''
            UPDATE notifications SET user_id=?, message=?, time=?, is_read=?
            WHERE id=?
            ''', (self.user_id, self.message, self.time, self.is_read, self.id))
        else:
            cursor.execute('''
            INSERT INTO notifications (user_id, message, time, is_read)
            VALUES (?, ?, ?, ?)
            ''', (self.user_id, self.message, self.time, self.is_read))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()
