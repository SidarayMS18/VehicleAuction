# api.py
from flask import Blueprint, jsonify, request, session
from models import User, Vehicle, Bid, Notification
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/check-auth', methods=['GET'])
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
    if user and user.password == data['password']:
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
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        password=data['password'],
        email=data['email']
    )
    user.save()
    return jsonify({'success': True})

@api.route('/vehicles', methods=['GET'])
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

@api.route('/notifications', methods=['GET'])
def get_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notifications = Notification.get_for_user(session['user_id'], unread_only=True)
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

@api.route('/bid', methods=['POST'])
def place_bid():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    vehicle = Vehicle.get_by_id(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    if datetime.strptime(vehicle.end_time, '%Y-%m-%d %H:%M:%S') < datetime.now():
        return jsonify({'error': 'Auction has ended'}), 400
    
    highest_bid = Bid.get_highest_for_vehicle(data['vehicle_id'])
    if highest_bid and data['amount'] <= highest_bid.amount:
        return jsonify({'error': 'Bid must be higher than current highest bid'}), 400
    
    if data['amount'] < vehicle.reserve_price:
        return jsonify({'error': 'Bid must be at least the reserve price'}), 400
    
    bid = Bid(
        amount=data['amount'],
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        bidder_id=session['user_id'],
        vehicle_id=data['vehicle_id']
    )
    bid.save()
    
    # Notify seller
    notification = Notification(
        user_id=vehicle.seller_id,
        message=f"New bid of ${data['amount']} placed on your {vehicle.make} {vehicle.model}",
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    notification.save()
    
    return jsonify({'success': True})

@api.route('/admin/vehicles', methods=['POST'])
def add_vehicle():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    # Convert HTML5 datetime-local format (YYYY-MM-DDTHH:MM) to SQLite compatible format (YYYY-MM-DD HH:MM:SS)
    end_time_str = data['end_time']
    if 'T' in end_time_str:
        end_time_str = end_time_str.replace("T", " ") + ":00"
    
    vehicle = Vehicle(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        mileage=data['mileage'],
        description=data.get('description', ''),
        reserve_price=data['reserve_price'],
        end_time=end_time_str,
        seller_id=session['user_id']
    )
    vehicle.save()
    return jsonify({'success': True, 'id': vehicle.id})
