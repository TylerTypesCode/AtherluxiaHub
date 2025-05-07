from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.Models import Notification
from app.instances import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify({
        'notifications': [{
            'id': notif.id,
            'message': notif.message,
            'read': notif.read,
            'created_at': notif.created_at.isoformat()
        } for notif in notifications]
    }), 200

@notification_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200

@notification_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read=False
    ).all()
    
    for notification in notifications:
        notification.read = True
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200