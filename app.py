from enum import Enum
from os import abort
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, InputRequired






#Flask Instance
app = Flask(__name__)

secret_key = secrets.token_hex(32)
#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/ptr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'MyDB'


#Initialize Database
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)

    
    
#Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from API.api import user_api
app.register_blueprint(user_api)
from models import Users,Category,Tournament,Judge,Athlete,Poomsae



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check Pass_hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                # Check if there is a stored URL in the session
                if 'next' in session:
                    # Redirect the user to the stored URL
                    return redirect(session['next'])
                # If there is no stored URL, redirect to the dashboard
                return redirect(url_for('index'))
            else:
                flash("Wrong password - Try Again!")
        else:
            flash("That user doesn't exist")
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/admin_dashboard", methods = ['GET', 'POST'])
@login_required
def dashboard():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("dashboard_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")

@app.route("/get_users", methods = ['GET'])
@login_required
def get_users():
    users = Users.query.all()
    return render_template('users_admin_page.html', users=users)

@app.route("/get_judges", methods = ['GET'])
def get_judges():
    judges = Judge.query.all()
    return render_template('users_admin_page.html', judges=judges)

@app.route("/get_tournaments", methods = ['GET'])
def get_tournaments():
    tournaments = Tournament.query.all()
    return render_template('users_admin_page.html', tournaments=tournaments)

@app.route("/get_category", methods = ['GET'])
def get_category():
    category = Category.query.all()
    return render_template('users_admin_page.html', category=category)

@app.route("/create_user", methods = ['GET', 'POST'])
def create_user():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            user = Users(username = form.username.data, real_name = form.real_name.data, password_hash = hashed_pw, user_type = 'user')
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash("Registado com sucesso!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("create_user.html", username=username, form=form, our_users=our_users)

@app.route("/update_user/<int:id>", methods = ['GET', 'POST'])
def update_user(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        print(request.form)
        user_to_update.username = request.form['username']
        user_to_update.real_name = request.form['real_name']
        user_to_update.password_hash = request.form['password_hash']   
        user_to_update.password_hash2 = request.form['password_hash2'] 
        if(user_to_update.password_hash != user_to_update.password_hash2) :
            flash("Passwords não são iguais!")
            return render_template("update.html", form=form, user_to_update = user_to_update, id = id)
        user_to_update.password_hash = generate_password_hash(user_to_update.password_hash,"sha256") 
        user_to_update.password_hash2 = generate_password_hash(user_to_update.password_hash,"sha256") 
        try:
            
            db.session.commit()
            flash("User Updated sucessfully")
            return render_template("update.html", form=form, user_to_update = user_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update.html", form=form, user_to_update = user_to_update, id = id)
    else:
        return render_template("update.html", form=form, user_to_update = user_to_update, id = id)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted sucessfully!")
        our_users = Users.query.order_by(Users.date_added)
        return redirect(url_for('create_user'))
    except: 
        flash("There was a prbolem deleting user, try again!")
        return redirect(url_for('get_users'))

@app.route('/juri_interface', methods = ['GET'])
@login_required
def judgeInterface():
    if current_user.user_type not in ['admin', 'judge','superadmin']:
        abort(403)
    return render_template("juriInterface.html")

@app.route('/create_judge' , methods=['GET', 'POST'])
def create_judge():
    form = JudgeForm()
    username = None
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(username=form.username.data).first()
        category = Category.query.filter_by(name=form.category_name.data).first()
        tournament = Tournament.query.filter_by(id = form.tournament_id.data).first()
        if user is None:
            user = Users(username=form.username.data, real_name=form.real_name.data, password_hash=hashed_pw, user_type= 'judge')
            db.session.add(user)
            db.session.commit()
        if category is None:
            category = Category(name=form.category_name.data)
            db.session.add(category)
            db.session.commit()
        if tournament is None:
            tournament = Tournament(name = form.category_name.data + "tournament")
            db.session.add(tournament)
            db.session.commit()
        
        judge = Judge(user=user, category_name=category.name, tournament_id=form.tournament_id.data, type_of_jury=form.type_of_jury.data)
        username = form.username.data
        form.username.data = ''
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''

        db.session.add(user)
        db.session.add(judge)
        db.session.commit()
        flash("Created Sucessefully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("create_judge.html", username=username, form=form, our_users=our_users)

@app.route('/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if current_user.user_type != 'superadmin':
        abort(403) # forbidden
    username = None
    form = AdminForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            form.user_type.data = form.type_of_admin
            user = Users(username = form.username.data, password_hash = hashed_pw, user_type = form.user_type.data)
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.user_perms.data = ''
        flash("Registado com sucesso!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("create_admin.html", username=username, form=form, our_users=our_users)



class UserType(Enum):
    user = 'user'
    jury = 'jury'
    admin = 'admin'
    athlete = 'athlete'
    


class TournamentForm(FlaskForm):
	name = StringField("name:", validators=[DataRequired()])


class UserForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    real_name= StringField("Real Name: ", validators=[DataRequired()])
    password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")


class JudgeForm(UserForm):
    type_of_jury = SelectField('Type of Jury', choices=[('normal', 'Normal'), ('major', 'Major')], default='normal')
    category_name = StringField('Category Name')
    tournament_id = IntegerField('ID do torneio')
    submit = SubmitField('Submit')

class AthleteForm(UserForm):
	age = IntegerField('Age:', validators =[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
    
class AdminForm(UserForm):
    type_of_admin = SelectField('Type of Admin', choices = [('admin', 'Admin' , ('superadmin', 'Superadmin'))], default = 'admin')


with app.app_context():
    db.create_all()
    admin_user = Users.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = Users(username='admin',
        real_name='Admin User',
        password_hash = generate_password_hash("admin", "sha256"),
        user_type='admin')
        tournament = Tournament(name = "tournament1")
        db.session.add(tournament)
        db.session.commit()
        db.session.add(admin_user)
        db.session.commit()