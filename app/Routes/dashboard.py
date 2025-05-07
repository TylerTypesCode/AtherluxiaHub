from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.Models import Game, Vote, Comment
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    # Get basic stats for developer's games
    games = Game.query.filter_by(developer_id=current_user.id).all()
    total_games = len(games)
    
    # Calculate total votes across all games
    total_votes = Vote.query.filter(
        Vote.game_id.in_([game.id for game in games])
    ).count()
    
    # Calculate total comments across all games
    total_comments = Comment.query.filter(
        Comment.game_id.in_([game.id for game in games])
    ).count()
    
    # Get recent activity
    last_30_days = datetime.utcnow() - timedelta(days=30)
    recent_votes = Vote.query.filter(
        Vote.game_id.in_([game.id for game in games]),
        Vote.created_at >= last_30_days
    ).count()
    
    recent_comments = Comment.query.filter(
        Comment.game_id.in_([game.id for game in games]),
        Comment.created_at >= last_30_days
    ).count()
    
    return jsonify({
        'total_games': total_games,
        'total_votes': total_votes,
        'total_comments': total_comments,
        'recent_activity': {
            'votes_last_30_days': recent_votes,
            'comments_last_30_days': recent_comments
        }
    }), 200

@dashboard_bp.route('/dashboard/games', methods=['GET'])
@login_required
def get_developer_games():
    games = Game.query.filter_by(developer_id=current_user.id).all()
    
    return jsonify({
        'games': [{
            'id': game.id,
            'title': game.title,
            'status': game.status,
            'votes_count': len(game.votes),
            'comments_count': len(game.comments),
            'created_at': game.created_at.isoformat()
        } for game in games]
    }), 200

@dashboard_bp.route('/dashboard/game/<int:game_id>/analytics', methods=['GET'])
@login_required
def get_game_analytics(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.developer_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get vote trends
    last_30_days = datetime.utcnow() - timedelta(days=30)
    vote_trend = db.session.query(
        func.date(Vote.created_at).label('date'),
        func.count(Vote.id).label('count')
    ).filter(
        Vote.game_id == game_id,
        Vote.created_at >= last_30_days
    ).group_by(
        func.date(Vote.created_at)
    ).all()
    
    # Get comment trends
    comment_trend = db.session.query(
        func.date(Comment.created_at).label('date'),
        func.count(Comment.id).label('count')
    ).filter(
        Comment.game_id == game_id,
        Comment.created_at >= last_30_days
    ).group_by(
        func.date(Comment.created_at)
    ).all()
    
    return jsonify({
        'vote_trend': [{
            'date': str(trend.date),
            'count': trend.count
        } for trend in vote_trend],
        'comment_trend': [{
            'date': str(trend.date),
            'count': trend.count
        } for trend in comment_trend]
    }), 200