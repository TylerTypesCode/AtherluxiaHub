from . import db, datetime

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    vote_type = db.Column(db.Enum('upvote', 'downvote', name='vote_types'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_id', name='unique_user_game_vote'),
    )

    def __repr__(self):
        return f'<Vote {self.vote_type} by User {self.user_id} on Game {self.game_id}>'