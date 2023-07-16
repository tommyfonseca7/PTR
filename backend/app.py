from enum import Enum
from os import abort
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from backend.database import add_instance,delete_instance,commit_changes
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, InputRequired
from backend.models import Users,Category,Tournament,Judge,Athlete,Poomsae,app
from flask_socketio import join_room, leave_room, emit, SocketIO



    
    
#Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from backend.API.api import user_api
app.register_blueprint(user_api)

socketio = SocketIO(app)




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


@app.route("/admin", methods = ['GET', 'POST'])
@login_required
def admin():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("dashboard_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")
    
#####################################################

@app.route("/admin/tournaments", methods = ['GET', 'POST'])
@login_required
def tounaments_admin():
    form = TournamentForm()
    tournaments = Tournament.query.all()

    if form.validate_on_submit():
        name = form.name.data
        if Tournament.query.filter_by(name=name).first():
            return 'Tournament already exists'

        tournament = Tournament(name=name)
        add_instance(tournament)

    if current_user.user_type == "admin" or "superadmin":
        return render_template("tournaments_admin.html", form=form, tournaments = tournaments)
    else:
        flash("You are not an admin!")
        return render_template("index.html")
    
@app.route("/admin/categories", methods = ['GET', 'POST'])
@login_required
def categories_admin():
    form = CategoryForm()
    tournaments = Tournament.query.all()


    if form.validate_on_submit():
        name = form.name.data
        if CategoryForm.query.filter_by(name=name).first():
            return 'Category already exists'

        category = Category(name=name)
        add_instance(category)


    if current_user.user_type == "admin" or "superadmin":
        return render_template("categories_admin.html", form=form, tournaments=tournaments)
    else:
        flash("You are not an admin!")
        return render_template("index.html")
    
@app.route("/admin/categoryId", methods = ['GET', 'POST'])
@login_required
def categoryId_admin():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("category_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")


@app.route("/admin/athletes", methods = ['GET', 'POST'])
@login_required
def athletes_admin():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("athletes_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")


@app.route("/admin/judges", methods = ['GET', 'POST'])
@login_required
def judges_admin():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("judges_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")


@app.route("/admin/users", methods = ['GET', 'POST'])
@login_required
def users_admin():
    if current_user.user_type == "admin" or "superadmin":
        return render_template("judges_admin.html")
    else:
        flash("You are not an admin!")
        return render_template("index.html")       





@app.route("/get_users", methods = ['GET'])
@login_required
def get_users():
    users = Users.query.all()
    return render_template('users_admin_page.html', users=users)

@app.route("/provas" , methods = ['GET'])
def provas():
    tournaments = Tournament.query.all()
    category = Category.query.all()
    return render_template('provas.html', tournaments=tournaments, category=category)


@app.route("/get_judges", methods = ['GET'])
@login_required
def get_judges():
    judges = Judge.query.all()
    return render_template('judges_admin_page.html', judges=judges)

@app.route("/get_tournaments", methods = ['GET'])
@login_required
def get_tournaments():
    tournaments = Tournament.query.all()
    return render_template('tournaments_admin_page.html', tournaments=tournaments)

@app.route("/get_category", methods = ['GET'])
@login_required
def get_category():
    category = Category.query.all()
    return render_template('category_admin_page.html', category=category)

@app.route("/create_user", methods = ['GET', 'POST'])
def create_user():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            add_instance(Users,username = form.username.data, real_name = form.real_name.data, password_hash = hashed_pw, user_type = 'user')
        username = form.username.data
        form.username.data = ''
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash("Registado com sucesso!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("create_user.html", username=username, form=form, our_users=our_users)

@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data

        if Category.query.filter_by(name=name).first():
            return 'Category already exists'

        category = Category(name=name)
        add_instance(category)

        return 'Category created successfully'

    return render_template('create_category.html', form=form)

@app.route('/update_category/<int:id>', methods=['GET', 'POST'])
def update_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        commit_changes()
        return redirect(url_for('list_categories'))

    return render_template('update_category.html', form=form)

@app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        delete_instance(category)
        return redirect(url_for('list_categories'))

    return render_template('delete_category.html', category=category)

@app.route('/category')
def list_categories():
    categories = Category.query.all()
    return render_template('category.html', categories=categories)

@app.route('/certain_category')
def tournament_category():
    athletes = Athlete.query.all()
    judges = Judge.query.all()
    return render_template('tournament_category.html', athletes=athletes, judges=judges)




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
            
            commit_changes()
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
        delete_instance(user_to_delete)
        flash("User deleted sucessfully!")
        return redirect(url_for('create_user'))
    except: 
        flash("There was a prbolem deleting user, try again!")
        return redirect(url_for('get_users'))



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
            add_instance(user)
        if category is None:
            category = Category(name=form.category_name.data)
            add_instance(category)
        if tournament is None:
            tournament = Tournament(name = form.category_name.data + "tournament")
            add_instance(tournament)
        
        judge = Judge(user=user, category_name=category.name, tournament_id=form.tournament_id.data, type_of_jury=form.type_of_jury.data)
        username = form.username.data
        form.username.data = ''
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''

        add_instance(user,judge)
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
            add_instance(user)
        username = form.username.data
        form.real_name.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.user_perms.data = ''
        flash("Registado com sucesso!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("create_admin.html", username=username, form=form, our_users=our_users)







########################################################################################################

@app.route('/lobby/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def lobby(tournament_id):
    active_tournament = Tournament.query.get(tournament_id)
    if active_tournament is None:
        abort(404)

    if current_user.user_type != 'admin':
        return redirect(url_for('judge_lobby', tournament_id=tournament_id))

    if request.method == 'POST' and 'start_tournament' in request.form:
        # Start the tournament and redirect to the judge interface
        active_tournament.active = True
        commit_changes()
        return redirect(url_for('judgeInterface', tournament_id=tournament_id))

    return render_template("lobby.html", tournament=active_tournament)


@app.route('/judge_lobby/<int:tournament_id>')
@login_required
def judge_lobby(tournament_id):
    active_tournament = Tournament.query.get(tournament_id)
    if active_tournament is None:
        abort(404)

    if current_user.user_type == 'admin':
        return redirect(url_for('lobby', tournament_id=tournament_id))

    return render_template("judge_lobby.html", tournament=active_tournament)


socketio.on('connect')
def on_connect():
    # Join the appropriate SocketIO room based on the user type and tournament
    if current_user.user_type == 'admin':
        join_room(f'admin_room_{current_user.id}')
    elif current_user.user_type == 'judge':
        tournament_id = request.args.get('tournament_id', type=int)
        if tournament_id:
            join_room(f'judge_room_{tournament_id}_{current_user.id}')


@socketio.on('disconnect')
def on_disconnect():
    # Leave the room on disconnect
    if current_user.user_type == 'admin':
        leave_room(f'admin_room_{current_user.id}')
    elif current_user.user_type == 'judge':
        tournament_id = request.args.get('tournament_id', type=int)
        if tournament_id:
            leave_room(f'judge_room_{tournament_id}_{current_user.id}')


@socketio.on('start_tournament')
def start_tournament(data):
    if current_user.user_type == 'admin':
        tournament_id = data.get('tournament_id')
        active_tournament = Tournament.query.get(tournament_id)
        if active_tournament:
            active_tournament.active = True
            commit_changes()
            emit('tournament_started', broadcast=True)

@app.route('/juri_interface', methods=['GET', 'POST'])
@login_required
def judgeInterface():
    global active_athlete
    if current_user.user_type not in ['admin', 'judge', 'superadmin']:
        abort(403)

    active_tournament = None
    for tournament in Tournament.query.all():
        if tournament.active:
            active_tournament = tournament
            break
    if active_tournament is None:
        return render_template("notournament.html")

    if not session.get('tournament_active', False):
        return redirect(url_for('lobby')) 


    if request.method == 'POST':
        data = request.get_json()
        strength_and_velocity = data.get('strength_and_velocity')
        rythm_and_coordenation = data.get('rhythm_and_coordination')
        energy_expression = data.get('energy_expression')
        technical_component = data.get('technical_component')
        athlete = data.get('name')
        tournament_id = data.get('tournament_id')
        results = Poomsae(
        name = athlete,
        tournament_id = tournament_id,
        strength_and_velocity=strength_and_velocity,
        rythm_and_coordenation=rythm_and_coordenation,
        energy_expression=energy_expression,
        technical_component=technical_component
    )
    
        add_instance(results)
        active_athlete.list_of_poomsaes.append(results)
        commit_changes()
        next_active_athlete = Athlete.query.filter(Athlete.id > active_athlete.id).first()

        if next_active_athlete != None:
                # Set the next athlete as active
                active_athlete.active = False
                next_active_athlete.active = True
                commit_changes()
                return redirect(url_for('judgeInterface'))
        active_athlete.active = False
        print(active_athlete.active)
        commit_changes()
        

        socketio.emit('evaluation_submitted', {
            'athlete_name': athlete.name,
            'tournament_name': active_tournament.name,
            'evaluation': {
                'strength_and_velocity': strength_and_velocity,
                'rythm_and_coordenation': rythm_and_coordenation,
                'energy_expression': energy_expression,
                'technical_component': technical_component
            }
        }, room=current_user.id)

        submitted_count = session.get('submitted_count', 0)
        submitted_count += 1
        session['submitted_count'] = submitted_count

        if submitted_count == len(active_tournament.list_of_judges.all()):
            session.pop('submitted_count')  # Reset the submitted count

            next_active_athlete = Athlete.query.filter(Athlete.id > active_athlete.id).first()

            if next_active_athlete is not None:
                active_athlete.active = False
                next_active_athlete.active = True
                commit_changes()

                socketio.emit('next_athlete', {'athlete_name': next_active_athlete.name, 'tournament_name': active_tournament.name},
                             broadcast=True)

    return render_template("judge_interface.html", active_athlete=active_athlete, tournament=active_tournament)



########################################################################################################


class UserType(Enum):
    user = 'user'
    jury = 'jury'
    admin = 'admin'
    athlete = 'athlete'
    



     

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
    
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Create Category')

class TournamentForm(FlaskForm):
    submit = SubmitField('Criar Troneio')
    name = StringField('Nome do Torneio: ', validators=[DataRequired()])