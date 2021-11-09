import os

# Database initialization
basedir = os.path.abspath(os.path.dirname(__file__))

# --- Local database
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# --- Postgres database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:a@localhost/appflask'


SQLALCHEMY_TRACK_MODIFICATIONS = False