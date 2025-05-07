from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.Models import Game, Vote, Comment, Tag
from app.instances import db
from datetime import datetime

game_bp = Blueprint('game', __name__)

@game_bp.route('/submit', methods=['POST'])
@login_required
def submit_game():
    data = request.get_json()
    
    if not all(k in data for k in ["title", "description", "genre", "platforms"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    game = Game(
        title=data['title'],
        description=data['description'],
        developer_id=current_user.id,
        genre=data['genre'],
        platforms=data['platforms'],
        cover_image_url=data.get('cover_image_url'),
        release_date=datetime.strptime(data['release_date'], '%Y-%m-%d') if data.get('release_date') else None,
        status='pending'
    )
    
    # Add tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                game.tags.append(tag)
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify({
        "message": "Game submitted successfully",
        "game_id": game.id
    }), 201

@game_bp.route('/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    return jsonify({
        "id": game.id,
        "title": game.title,
        "description": game.description,
        "genre": game.genre,
        "platforms": game.platforms,
        "cover_image_url": game.cover_image_url,
        "release_date": game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
        "developer": {
            "id": game.developer.id,
            "username": game.developer.username
        },
        "votes_count": len(game.votes),
        "comments_count": len(game.comments),
        "tags": [tag.name for tag in game.tags],
        "created_at": game.created_at.isoformat(),
        "updated_at": game.updated_at.isoformat()
    }), 200

@game_bp.route('/<int:game_id>', methods=['PUT'])
@login_required
def update_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.developer_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        game.title = data['title']
    if 'description' in data:
        game.description = data['description']
    if 'genre' in data:
        game.genre = data['genre']
    if 'platforms' in data:
        game.platforms = data['platforms']
    if 'cover_image_url' in data:
        game.cover_image_url = data['cover_image_url']
    if 'release_date' in data:
        game.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d')
    
    if 'tags' in data and isinstance(data['tags'], list):
        game.tags = []
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                game.tags.append(tag)
    
    db.session.commit()
    
    return jsonify({"message": "Game updated successfully"}), 200

@game_bp.route('/list', methods=['GET'])
def list_games():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    genre = request.args.get('genre')
    
    query = Game.query.filter_by(status='approved')
    
    if genre:
        query = query.filter_by(genre=genre)
    
    games = query.order_by(Game.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        "total": games.total,
        "pages": games.pages,
        "current_page": games.page,
        "games": [{
            "id": game.id,
            "title": game.title,
            "genre": game.genre,
            "cover_image_url": game.cover_image_url,
            "votes_count": len(game.votes),
            "developer": game.developer.username
        } for game in games.items]
    }), 200