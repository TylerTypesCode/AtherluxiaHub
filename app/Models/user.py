from . import db, datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.Enum('admin', 'developer', 'user', name='user_roles'), default='user')
    bio = db.Column(db.Text, nullable=True)
    profile_picture_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    games = db.relationship('Game', backref='developer', lazy=True)
    votes = db.relationship('Vote', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    # Follow relationship (self-referential)
    following = db.relationship(
        'User', secondary='follows',
        primaryjoin='User.id==follows.c.follower_id',
        secondaryjoin='User.id==follows.c.followed_id',
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'