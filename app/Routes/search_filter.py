from flask import Blueprint, request, jsonify
from app.Models import Game, Tag, User
from sqlalchemy import or_
from app.instances import db

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    platform = request.args.get('platform', None)
    genre = request.args.get('genre', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query
    base_query = Game.query.filter_by(status='approved')
    
    # Apply search filters
    if query:
        base_query = base_query.filter(
            or_(
                Game.title.ilike(f'%{query}%'),
                Game.description.ilike(f'%{query}%')
            )
        )
    
    # Apply category filters
    if category != 'all':
        if category == 'trending':
            # Order by vote count
            base_query = base_query.order_by(db.func.count(Game.votes).desc())
        elif category == 'newest':
            base_query = base_query.order_by(Game.created_at.desc())
    
    # Apply platform filter
    if platform:
        base_query = base_query.filter(Game.platforms.ilike(f'%{platform}%'))
    
    # Apply genre filter
    if genre:
        base_query = base_query.filter(Game.genre == genre)
    
    # Execute pagination
    results = base_query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': results.total,
        'pages': results.pages,
        'current_page': results.page,
        'games': [{
            'id': game.id,
            'title': game.title,
            'description': game.description,
            'developer': {
                'id': game.developer.id,
                'username': game.developer.username
            },
            'genre': game.genre,
            'platforms': game.platforms,
            'cover_image_url': game.cover_image_url,
            'votes_count': len(game.votes),
            'comments_count': len(game.comments),
            'tags': [tag.name for tag in game.tags]
        } for game in results.items]
    }), 200

@search_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'suggestions': []}), 200
    
    # Get game title suggestions
    game_suggestions = Game.query.filter(
        Game.title.ilike(f'%{query}%')
    ).limit(5).all()
    
    # Get tag suggestions
    tag_suggestions = Tag.query.filter(
        Tag.name.ilike(f'%{query}%')
    ).limit(5).all()
    
    return jsonify({
        'suggestions': {
            'games': [{
                'id': game.id,
                'title': game.title,
                'type': 'game'
            } for game in game_suggestions],
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'type': 'tag'
            } for tag in tag_suggestions]
        }
    }), 200

@search_bp.route('/filters', methods=['GET'])
def get_filters():
    # Get unique genres
    genres = db.session.query(Game.genre).distinct().all()
    
    # Get all tags
    tags = Tag.query.all()
    
    # Get unique platforms
    platforms = db.session.query(Game.platforms).distinct().all()
    
    return jsonify({
        'genres': [genre[0] for genre in genres if genre[0]],
        'tags': [{'id': tag.id, 'name': tag.name} for tag in tags],
        'platforms': list(set([
            platform.strip() 
            for platforms_str in platforms 
            for platform in platforms_str[0].split(',')
            if platform.strip()
        ]))
    }), 200