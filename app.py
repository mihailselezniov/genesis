#!flask/bin/python
import os, datetime, requests, time, xmltodict, json, redis
from flask import Flask, jsonify, abort, make_response, request, render_template
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


r_server = redis.Redis(host=os.getenv("IP", "0.0.0.0"), port=6379)
app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object('config')
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
admin = Admin(app, url="/admin")
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Cities(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), index=True)
    
    def __repr__(self):
        return "<cities({})>".format(self.name)


admin.add_view(ModelView(Cities, db.session))


from views import *


if __name__ == '__main__':
    manager.run()