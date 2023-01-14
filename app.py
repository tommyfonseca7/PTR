from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

#Flask Instance
app = Flask(__name__)

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/users'

app.config['SECRET_KEY'] = "random"
#Initialize Database
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    return render_template("login.html")

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
            user = Users(username= form.username.data, password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash("Resgitrado com sucesso! ")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("newuser.html", username=username, form=form, our_users=our_users)

@app.route("/updateuser/<int:id>", methods = ['GET', 'POST'])
def updateuser(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    
    return render_template("admin.html")








class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
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


class UserForm(FlaskForm):
	username = StringField("Username:", validators=[DataRequired()])
	password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

