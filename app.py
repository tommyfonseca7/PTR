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






class UserForm(FlaskForm):
	username = StringField("Username:", validators=[DataRequired()])
	password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
	user_perms = IntegerField('User Permissions (1 or 2)', validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

