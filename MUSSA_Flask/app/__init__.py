from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir

oid = OpenID(app, os.path.join(basedir, 'tmp'))

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models
