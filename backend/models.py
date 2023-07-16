from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.init import create_app

app = create_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(200), nullable=False, unique=True)
    real_name = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.Enum('user', 'judge', 'admin', 'superadmin', 'athlete'), default='user')

class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    

class Tournament(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    active = db.Column(db.Boolean, default= True)
    list_of_judges = db.relationship('Judge', lazy='dynamic')
    list_of_athletes = db.relationship('Athlete', lazy='dynamic')

class Judge(db.Model):
    __tablename__ = 'judge'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, primary_key=True)
    user = db.relationship('Users', backref=db.backref('judge', uselist=False))
    category_name = db.Column(db.String(200), db.ForeignKey('category.name'), unique=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), unique=True)
    type_of_jury = db.Column(db.Enum('major', 'normal', default = 'normal'))


class Athlete(db.Model, UserMixin):
    __tablename__ = 'athlete'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category_type = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default= False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    list_of_poomsaes = db.relationship('Poomsae', secondary='athlete_poomsae')
    athlete_poomsae = db.Table('athlete_poomsae',
    db.Column('athlete_id', db.Integer, db.ForeignKey('athlete.id'), primary_key=True),
    db.Column('poomsae_id', db.Integer, db.ForeignKey('poomsae.id'), primary_key=True)
)


class Poomsae(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    strength_and_velocity = db.Column(db.Integer)
    rythm_and_coordenation = db.Column(db.Integer)
    energy_expression = db.Column(db.Integer)
    technical_component = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


    @property
    def password(self):
        raise AttributeError('password is not a readable atribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<NAME %r>' % self.username
    
    
    
with app.app_context():
    db.create_all()
    admin_user = Users.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = Users(username='admin',
        real_name='Admin User',
        password_hash = generate_password_hash("admin", "sha256"),
        user_type='admin')
        tournament = Tournament(name = "tournament1")
        db.session.add(admin_user)
        db.session.add(tournament)
        db.session.commit()


