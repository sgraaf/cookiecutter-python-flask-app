"""Extensions used by {{ cookiecutter.friendly_name }}."""

from flask_alembic import Alembic
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy_lite import SQLAlchemy

# database
db = SQLAlchemy()

# migrations
alembic = Alembic()

# user session management
login_manager = LoginManager()

# email sending
mail = Mail()
