from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
login_manager.needs_refresh_message = 'Session expired. Please log in again.'
login_manager.needs_refresh_message_category = 'info'
login_manager.refresh_view = 'auth.reauthenticate'

migrate = Migrate()
db = SQLAlchemy()
