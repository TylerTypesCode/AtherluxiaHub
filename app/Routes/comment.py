from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.Models import Comment, Game, Notification
from app.instances import db
from datetime import datetime

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/game/<int:game_id>/comment', methods=['POST'])
@login_required
def add_comment(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    if 'content' not in data or not data['content'].strip():
        return jsonify({"error": "Comment content is required"}), 400
        
    comment = Comment(
        user_id=current_user.id,
        game_id=game_id,
        content=data['content']
    )
    
    db.session.add(comment)
    
    # Create notification for game developer
    if game.developer_id != current_user.id:
        notification = Notification(
            user_id=game.developer_id,
            message=f"{current_user.username} commented on your game {game.title}"
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        "message": "Comment added successfully",
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "user": current_user.username,
            "created_at": comment.created_at.isoformat()
        }
    }), 201

@comment_bp.route('/game/<int:game_id>/comments', methods=['GET'])
def get_comments(game_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    comments = Comment.query.filter_by(game_id=game_id)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        "total": comments.total,
        "pages": comments.pages,
        "current_page": comments.page,
        "comments": [{
            "id": comment.id,
            "content": comment.content,
            "user": comment.user.username,
            "created_at": comment.created_at.isoformat()
        } for comment in comments.items]
    }), 200