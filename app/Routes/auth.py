from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from app.instances import login_manager
from werkzeug.security import check_password_hash
from app.Models import User
from app.instances import db

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            "message": "Logged in successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200