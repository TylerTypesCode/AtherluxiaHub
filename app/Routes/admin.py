from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.Models import User, Game, Vote, Comment
from app.instances import db
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@admin_required
def get_admin_stats():
    # Get platform statistics
    total_users = User.query.count()
    total_games = Game.query.count()
    total_votes = Vote.query.count()
    total_comments = Comment.query.count()
    
    # Get pending game submissions
    pending_games = Game.query.filter_by(status='pending').count()
    
    # Get user growth stats for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    return jsonify({
        "platform_stats": {
            "total_users": total_users,
            "total_games": total_games,
            "total_votes": total_votes,
            "total_comments": total_comments,
            "pending_games": pending_games,
            "new_users_last_30_days": new_users
        }
    }), 200

@admin_bp.route('/games/pending', methods=['GET'])
@login_required
@admin_required
def get_pending_games():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pending_games = Game.query.filter_by(status='pending')\
        .order_by(Game.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        "total": pending_games.total,
        "pages": pending_games.pages,
        "current_page": pending_games.page,
        "games": [{
            "id": game.id,
            "title": game.title,
            "developer": game.developer.username,
            "submitted_at": game.created_at.isoformat(),
            "genre": game.genre
        } for game in pending_games.items]
    }), 200

@admin_bp.route('/games/<int:game_id>/review', methods=['POST'])
@login_required
@admin_required
def review_game(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    if 'status' not in data or data['status'] not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status"}), 400
    
    game.status = data['status']
    if 'feedback' in data:
        # Create notification for game developer
        notification = Notification(
            user_id=game.developer_id,
            message=f"Your game {game.title} has been {data['status']}. {data['feedback']}"
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        "message": f"Game {game.title} has been {data['status']}",
        "game_id": game.id,
        "status": game.status
    }), 200

@admin_bp.route('/users/manage', methods=['GET'])
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        "total": users.total,
        "pages": users.pages,
        "current_page": users.page,
        "users": [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
            "games_count": len(user.games)
        } for user in users.items]
    }), 200

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role' not in data or data['role'] not in ['admin', 'developer', 'user']:
        return jsonify({"error": "Invalid role"}), 400
    
    if user.id == current_user.id:
        return jsonify({"error": "Cannot modify own role"}), 403
    
    user.role = data['role']
    db.session.commit()
    
    return jsonify({
        "message": f"User {user.username} role updated to {user.role}",
        "user_id": user.id,
        "role": user.role
    }), 200

@admin_bp.route('/analytics/platform', methods=['GET'])
@login_required
@admin_required
def platform_analytics():
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily user registrations
    user_registrations = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= start_date)\
        .group_by(func.date(User.created_at))\
        .all()
    
    # Get daily game submissions
    game_submissions = db.session.query(
        func.date(Game.created_at).label('date'),
        func.count(Game.id).label('count')
    ).filter(Game.created_at >= start_date)\
        .group_by(func.date(Game.created_at))\
        .all()
    
    return jsonify({
        "user_growth": [{
            "date": str(reg.date),
            "registrations": reg.count
        } for reg in user_registrations],
        "game_submissions": [{
            "date": str(sub.date),
            "submissions": sub.count
        } for sub in game_submissions]
    }), 200