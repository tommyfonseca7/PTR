from backend.init import create_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = create_app()
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)
db.create_all()