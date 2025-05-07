from . import db, datetime

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    platforms = db.Column(db.String(200), nullable=False)
    cover_image_url = db.Column(db.String(256), nullable=True)
    release_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='game_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    votes = db.relationship('Vote', backref='game', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='game', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='game_tags', backref=db.backref('games', lazy=True))

    def __repr__(self):
        return f'<Game {self.title}>'