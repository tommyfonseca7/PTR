from backend.init import create_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = create_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

