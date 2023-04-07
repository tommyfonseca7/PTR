from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length

#Flask Instance
app = Flask(__name__)

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/users'

app.config['SECRET_KEY'] = "random"
#Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_perms = db.Column(db.Integer, nullable=False)

class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    listJury = db.relationship('Jury', backref = 'category')
    listAthletes = db.relationship('Athlete', backref = 'category')

class Tournament(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    listJury = db.relationship('Jury', backref = 'tournament')
    listAthletes = db.relationship('Athlete', backref = 'tournament')
    list_of_Poomsaes = db.relationship('Poomsae', backref = 'tournament')

class Jury(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    category_name = db.Column(db.String(200), db.ForeignKey('category.name'), nullable=False)
    tournament_id = db.Column(db.String(200), db.ForeignKey('tournament.id'), nullable=False)
    password_hash = db.Column(db.String(128))
    type_of_jury = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)



class Athlete(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    category_name = db.Column(db.String(200), db.ForeignKey('category.name'), nullable=False)
    tournament_id = db.Column(db.String(200), db.ForeignKey('tournament.id'), nullable=False)
    list_of_poomsaes = db.relationship('Poomsae', secondary='athlete_poomsae', backref='athlete')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    athlete_poomsae = db.Table('athlete_poomsae',
    db.Column('athlete_id', db.Integer, db.ForeignKey('athlete.id'), primary_key=True),
    db.Column('poomsae_id', db.Integer, db.ForeignKey('poomsae.id'), primary_key=True)
)


class Poomsae(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    tournament_id = db.Column(db.String(200), db.ForeignKey('tournament.id'), nullable=False)
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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check Pass_hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - Try Again!")
        else:
            flash("That user doesn't exist")
    return render_template("login.html", form=form)

@app.route("/juri_interface", methods = ['GET', 'POST'])
def juri_interface():
    return render_template("juriInterface.html")


@app.route("/dashboard", methods = ['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/newuser", methods = ['GET', 'POST'])
def newuser():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            user = Users(username= form.username.data, password_hash = hashed_pw, user_perms = form.user_perms.data)
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.user_perms.data = ''
        flash("Resgitrado com sucesso! ")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("newuser.html", username=username, form=form, our_users=our_users)

@app.route("/updateuser/<int:id>", methods = ['GET', 'POST'])
def updateuser(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.username = request.form['username']
        user_to_update.password_hash = generate_password_hash(request.form['password_hash'], "sha256")
        user_to_update.user_perms = request.form['user_perms']         
        try:
            db.session.commit()
            flash("User Updated sucessfully")
            return render_template("update.html", form=form, user_to_update = user_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update.html", form=form, user_to_update = user_to_update, id = id)
    else:
        return render_template("update.html", form=form, user_to_update = user_to_update, id = id)

@app.route('/deleteuser/<int:id>')
def deleteuser(id):
    username = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted sucessfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("newuser.html", form=form, username=username, user_to_delete = user_to_delete, our_users=our_users)
    except: 
        flash("There was a prbolem deleting user, try again!")
        return render_template("update.html", form=form, username=username, user_to_delete = user_to_delete, our_users=our_users)


def newAthlete():
    name = None
    form = AthleteForm()
    if form.validate_on_submit():
        athlete = Athlete.query.filter_by(name=form.name.data).first()
        if athlete is None:
            athlete = Athlete(name = form.name.data,list_of_poomsaes = form.list_of_poomsaes.data, age = form.age.data)
            db.session.add(athlete)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.list_of_poomsaes.data = ''
        form.age.data = ''
        flash("Athlete registered sucessfully!")
    our_athletes = Athlete.query.order_by(Users.date_added)
    return render_template("newathlete.html", name=name, form=form, our_athletes=our_athletes)


@app.route("/updateathlete/<int:id>", methods = ['GET', 'POST'])
def updateAthlete(id):
    form = AthleteForm()
    athlete_to_update = Athlete.query.get_or_404(id)
    if request.method == "POST":
        athlete_to_update.name = request.form['name']
        athlete_to_update.list_of_poomsaes = request.form['list_of_poomsaes']
        athlete_to_update.age = request.form['age']         
        try:
            db.session.commit()
            flash("Athlete Updated sucessfully")
            return render_template("update.html", form=form, athlete_to_update = athlete_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update.html", form=form, athlete_to_update = athlete_to_update, id = id)
    else:
        return render_template("update.html", form=form, athlete_to_update = athlete_to_update, id = id)


@app.route('/deleteathlete/<int:id>')
def deleteathlete(id):
    name = None
    form = AthleteForm()
    athlete_to_delete = Athlete.query.get_or_404(id)
    try:
        db.session.delete(athlete_to_delete)
        db.session.commit()
        flash("Athlete deleted sucessfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("newathlete.html", form=form, name=name, athlete_to_delete = athlete_to_delete, our_athletes=our_athletes)
    except: 
        flash("There was a prbolem deleting the athlete, try again!")
        return render_template("update.html", form=form, name=name, athlete_to_delete = athlete_to_delete, our_athletes=our_athletes)


def newjury():
    username = None
    form = JuryForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        jury = Jury.query.filter_by(username=form.username.data).first()
        if jury is None:
            jury = Athlete(username= form.username.data, password_hash = hashed_pw, type_of_jury = form.type_of_jury.data)
            db.session.add(jury)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.type_of_jury.data = ''
        flash("Jury registered sucessfully!")
    our_jurys = Jury.query.order_by(Users.date_added)
    return render_template("newjury.html", username=username, form=form, our_jurys=our_jurys)


@app.route("/updatejury/<int:id>", methods = ['GET', 'POST'])
def updatejury(id):
    form = JuryForm()
    jury_to_update = Jury.query.get_or_404(id)
    if request.method == "POST":
        jury_to_update.username = request.form['username']
        jury_to_update.password_hash = generate_password_hash(request.form['password_hash'], "sha256")
        jury_to_update.type_of_jury = request.form['type_of_jury']         
        try:
            db.session.commit()
            flash("Jury Updated sucessfully")
            return render_template("update.html", form=form, jury_to_update = jury_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update.html", form=form, jury_to_update = jury_to_update, id = id)
    else:
        return render_template("update.html", form=form, jury_to_update = jury_to_update, id = id)


@app.route('/deletejury/<int:id>')
def deletejury(id):
    username = None
    form = JuryForm()
    jury_to_delete = Jury.query.get_or_404(id)
    try:
        db.session.delete(jury_to_delete)
        db.session.commit()
        flash("Jury deleted sucessfully!")
        our_jurys = Jury.query.order_by(Jury.date_added)
        return render_template("newjury.html", form=form, username=username, jury_to_delete = jury_to_delete, our_jurys=our_jurys)
    except: 
        flash("There was a prbolem deleting user, try again!")
        return render_template("update.html", form=form, username=username, jury_to_delete = jury_to_delete, our_jurys=our_jurys)


def newPoomsae():
    name = None
    form = JuryForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        Jury = Athlete.query.filter_by(username=form.username.data).first()
        if athlete is None:
            athlete = Athlete(username= form.username.data, password_hash = hashed_pw, user_perms = form.user_perms.data, type_of_jury = form.type_of_jury.data)
            db.session.add(athlete)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.user_perms.data = ''
        form.type_of_jury.data = ''
        flash("Jury registered sucessfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("newjury.html", username=username, form=form, our_users=our_users)








class TournamentForm(FlaskForm):
	name = StringField("name:", validators=[DataRequired()])


class JuryForm(FlaskForm):
	username = StringField("Username:", validators=[DataRequired()])
	password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
	type_of_jury = StringField("Type:", validators=[DataRequired()])
	submit = SubmitField("Submit")

class UserForm(FlaskForm):
	username = StringField("Username:", validators=[DataRequired()])
	password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
	user_perms = IntegerField('User Permissions (1 or 2)', validators=[DataRequired()])
	submit = SubmitField("Submit")

class AthleteForm(FlaskForm):
	username = StringField("Username:", validators=[DataRequired()])
	password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
	age = IntegerField('Age:', validators =[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
    

