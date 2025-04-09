from flask import Blueprint, jsonify, request, session
from models import User, Vehicle, Bid, Notification
from datetime import datetime
import sqlite3

api = Blueprint('api', __name__)

@api.route('/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'id': session['user_id'],
            'username': session['username'],
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'error': 'Not authenticated'}), 401

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.find_by_username(data['username'])
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return jsonify({
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.find_by_username(data['username']):
        return jsonify({'error': 'Username exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    user.save()
    return jsonify({'success': True})

@api.route('/vehicles')
def get_vehicles():
    vehicles = Vehicle.get_all_active()
    result = []
    for v in vehicles:
        highest_bid = Bid.get_highest_for_vehicle(v.id)
        result.append({
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'mileage': v.mileage,
            'reserve_price': v.reserve_price,
            'end_time': v.end_time,
            'highest_bid': highest_bid.amount if highest_bid else None
        })
    return jsonify(result)

@api.route('/bid', methods=['POST'])
def place_bid():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    vehicle = Vehicle.get_by_id(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    if datetime.strptime(vehicle.end_time, '%Y-%m-%d %H:%M:%S') < datetime.now():
        return jsonify({'error': 'Auction ended'}), 400
    
    highest_bid = Bid.get_highest_for_vehicle(data['vehicle_id'])
    if highest_bid and data['amount'] <= highest_bid.amount:
        return jsonify({'error': 'Bid too low'}), 400
    
    if data['amount'] < vehicle.reserve_price:
        return jsonify({'error': 'Below reserve'}), 400
    
    bid = Bid(
        amount=data['amount'],
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        bidder_id=session['user_id'],
        vehicle_id=data['vehicle_id']
    )
    bid.save()
    
    Notification(
        user_id=vehicle.seller_id,
        message=f"New bid ${data['amount']} on {vehicle.make} {vehicle.model}",
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ).save()
    
    return jsonify({'success': True})

@api.route('/notifications')
def get_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notifications = Notification.get_for_user(session['user_id'], True)
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'time': n.time
    } for n in notifications])

@api.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notification = Notification(id=notification_id)
    notification.mark_as_read()
    return jsonify({'success': True})

@api.route('/admin/vehicles', methods=['POST'])
def add_vehicle():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    end_time = data['end_time'].replace("T", " ") + ":00"
    
    vehicle = Vehicle(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        mileage=data['mileage'],
        description=data.get('description', ''),
        reserve_price=data['reserve_price'],
        end_time=end_time,
        seller_id=session['user_id']
    )
    vehicle.save()
    return jsonify({'success': True, 'id': vehicle.id})

@api.route('/admin/vehicles/edit/<int:vehicle_id>', methods=['POST'])
def edit_vehicle(vehicle_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    vehicle = Vehicle.get_by_id(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    vehicle.make = data.get('make', vehicle.make)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.year = data.get('year', vehicle.year)
    vehicle.mileage = data.get('mileage', vehicle.mileage)
    vehicle.description = data.get('description', vehicle.description)
    vehicle.reserve_price = data.get('reserve_price', vehicle.reserve_price)
    
    if 'end_time' in data:
        vehicle.end_time = data['end_time'].replace("T", " ") + ":00"
    
    vehicle.save()
    return jsonify({'success': True})

@api.route('/admin/vehicles/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bids WHERE vehicle_id=?", (vehicle_id,))
    cursor.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@api.route('/profile')
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.find_by_username(session['username'])
    return jsonify({
        'username': user.username,
        'email': user.email,
        'balance': user.balance
    })

@api.route('/profile/add-funds', methods=['POST'])
def add_funds():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    try:
        amount = float(data.get('amount', 0))
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    user = User.find_by_username(session['username'])
    user.balance += amount
    user.save()
    return jsonify({'success': True, 'new_balance': user.balance})

@api.route('/admin/users')
def get_all_users():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, balance, is_admin FROM users")
    users = [dict(zip(['id','username','email','balance','is_admin'], row)) 
            for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)
