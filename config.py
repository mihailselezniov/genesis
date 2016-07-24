import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = 'app.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, db_name)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
