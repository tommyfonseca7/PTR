from flask import Flask

from flask_sqlalchemy import SQLAlchemy
import secrets


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    secret_key = secrets.token_hex(32)
    #Add Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/ptr'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = secret_key
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'admin'
    app.config['MYSQL_DB'] = 'MyDB'
    return app

