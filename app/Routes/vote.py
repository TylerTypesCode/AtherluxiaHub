from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.Models import Vote, Game
from app.instances import db
from datetime import datetime

vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/game/<int:game_id>/vote', methods=['POST'])
@login_required
def vote_game(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    if 'vote_type' not in data or data['vote_type'] not in ['upvote', 'downvote']:
        return jsonify({"error": "Invalid vote type"}), 400
    
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        game_id=game_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == data['vote_type']:
            db.session.delete(existing_vote)
            db.session.commit()
            return jsonify({"message": "Vote removed"}), 200
        else:
            existing_vote.vote_type = data['vote_type']
            db.session.commit()
            return jsonify({"message": "Vote updated"}), 200
    
    new_vote = Vote(
        user_id=current_user.id,
        game_id=game_id,
        vote_type=data['vote_type']
    )
    
    db.session.add(new_vote)
    db.session.commit()
    
    return jsonify({"message": "Vote recorded successfully"}), 201