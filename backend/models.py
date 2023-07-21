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
    real_name = db.Column(db.String(200), nullable=False, unique=False)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.Enum('user', 'judge', 'admin', 'superadmin', 'athlete'), default='user')

class Tournament(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    active = db.Column(db.Boolean, default= True)
    list_of_categories = db.relationship('Category', lazy='dynamic')
    

class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable = False)
    tournament = db.relationship('Tournament', back_populates='list_of_categories')
    list_of_athletes = db.relationship('Athlete', lazy='dynamic')
    list_of_judges = db.relationship('Judge', lazy='dynamic')
    


class Judge(db.Model):
    __tablename__ = 'judge'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, primary_key=True)
    user = db.relationship('Users', backref=db.backref('judge', uselist=False))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), unique=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), unique=False)
    type_of_jury = db.Column(db.Enum('major', 'normal', default = 'normal'))


class Athlete(db.Model, UserMixin):
    __tablename__ = 'athlete'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    active = db.Column(db.Boolean, default= False)
    list_of_poomsaes = db.relationship('Poomsae', secondary='athlete_poomsae')
    poomsae_median = db.Column(db.Double)
    athlete_poomsae = db.Table('athlete_poomsae',
    db.Column('athlete_id', db.Integer, db.ForeignKey('athlete.id'), primary_key=True),
    db.Column('poomsae_id', db.Integer, db.ForeignKey('poomsae.id'), primary_key=True))
    rank = db.Column(db.Integer)


class Poomsae(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    strength_and_velocity = db.Column(db.Double)
    rythm_and_coordenation = db.Column(db.Double)
    energy_expression = db.Column(db.Double)
    technical_component = db.Column(db.Double)
    presentation_component = db.Column(db.Double)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    median = db.Column(db.Double)



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
    category = Category(name = "")
    if not admin_user:
        admin_user = Users(username='admin',
        real_name='Admin User',
        password_hash = generate_password_hash("admin", "sha256"),
        user_type='admin')
        tournament = Tournament(name = "Open da Lusofona")
        db.session.add(admin_user)
        db.session.add(tournament)
        
        category1 = Category(name = "SUB14 DAN M", tournament_id = 1)
        category2 = Category(name = "SUB14 DAN F", tournament_id = 1)
        category3 = Category(name = "SUB17 DAN M", tournament_id = 1)
        category4 = Category(name = "SUB17 DAN F", tournament_id = 1)
        category5 = Category(name = "SUB30 DAN M", tournament_id = 1)
        category6 = Category(name = "SUB30 DAN F", tournament_id = 1)
        category7 = Category(name = "SUB40 DAN M", tournament_id = 1)
        category8 = Category(name = "SUB40 DAN F", tournament_id = 1)
        
       
        db.session.add(category1)
        db.session.add(category2)
        db.session.add(category3)
        db.session.add(category4)
        db.session.add(category5)
        db.session.add(category6)
        db.session.add(category7)
        db.session.add(category8)
        
        db.session.commit()


