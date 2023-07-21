from enum import Enum
from os import abort
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from backend.database import add_instance,delete_instance,commit_changes
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, InputRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from backend.models import Users,Category,Tournament,Judge,Athlete,Poomsae,app
from flask_socketio import join_room, leave_room, emit, SocketIO
import logging

import uuid


    
#Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from backend.API.api import user_api
app.register_blueprint(user_api)





@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def index():
    tournaments = Tournament.query.all()
    return render_template("index.html", tournaments = tournaments)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                if 'next' in session:
                    return redirect(session['next'])
                if user.user_type == "judge":
                    return redirect(url_for("lobby"))
                if user.user_type == "admin" or user.user_type == "superadmin":
                    return redirect(url_for('admin'))
                else: 
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
    tournaments = Tournament.query.all()
    categories = Category.query.all()
    judges = Judge.query.all()
    users = Users.query.all()
    tournament_length = len(tournaments)
    categories_length = len(categories)
    judges_length = len(judges)
    users_length = len(users)
    if current_user.user_type == "admin" or "superadmin":
        return render_template("dashboard.html", tournaments=tournaments, categories=categories, judges=judges, users=users,
                                tournament_length=tournament_length, categories_length=categories_length, judges_length=judges_length,
                                  users_length=users_length )
    else:
        flash("You are not an admin!")
        return render_template("index.html")
    
#####################################################

@app.route("/admin/tournaments", methods = ['GET', 'POST'])
@login_required
def tournaments_admin():
    form = TournamentForm()
    tournaments = Tournament.query.all()
    

    if form.validate_on_submit():
        name = form.name.data
        if Tournament.query.filter_by(name=name).first():
            flash ('Tournament already exists')
            return redirect(url_for('tournaments_admin'))

        add_instance(Tournament, name = name)
        flash('Tournament created!')
        return redirect(url_for('tournaments_admin'))

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
    categories = Category.query.all()


    if form.validate_on_submit():
        name = form.name.data
        tournament = form.tournament.data
        tournament_id = tournament.id
        
        add_instance(Category, name=name, tournament_id=tournament_id, tournament = tournament)
        return redirect(url_for('categories_admin'))


    if current_user.user_type == "admin" or current_user.user_type == "superadmin":
        return render_template("categories_admin.html", form=form, tournaments=tournaments, categories=categories)
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
    
    form = AthleteForm()
    categories = Category.query.all()
    athletes = Athlete.query.all()
    tournament = Tournament.query.all()
    flash(" is validated!")

    
    if request.method == "POST":
            flash("Form is validated!")  
            name = form.name.data
            category = form.category.data
            category_id = category.id
            tournament = form.tournament.data
            tournament_id = tournament.id
            add_instance(Athlete, name=name, category_id=category_id, tournament_id = tournament_id, active = False)
            flash("New athlete added successfully!")  
            return redirect(url_for('athletes_admin'))

    if current_user.user_type == "admin" or current_user.user_type == "superadmin":
        return render_template("athletes_admin.html", form=form, athlete=athletes, categories=categories, tournament=tournament)
    else:
        flash("You are not an admin!")
        return render_template("index.html")


@app.route("/admin/judges", methods = ['GET', 'POST'])
@login_required
def judges_admin():
    
    tournaments = Tournament.query.all()
    categories = Category.query.all()
    judges = Judge.query.all()
    form = JudgeForm()
    
    if request.method == "POST":
            flash("Form is validated!") 
            user = Users.query.filter_by(username = form.username.data).first()
            username = form.username.data
            real_name = form.real_name.data
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            type_of_jury = form.type_of_jury.data
            category = form.category.data
            tournament = form.tournament.data
            category_id = category.id
            tournament_id = tournament.id
            if user is None:
                add_instance(Users,username = username, real_name = real_name, password_hash = hashed_pw, user_type = 'Judge')
            user = Users.query.filter_by(username = form.username.data).first()
            add_instance(Judge, user = user, id = user.id, category_id = category_id, tournament_id = tournament_id, type_of_jury = type_of_jury)
            flash("New athlete added successfully!") 
            return redirect(url_for('judges_admin'))
    

    if current_user.user_type == "admin" or "superadmin":
        return render_template("judges_admin.html", form=form, tournaments = tournaments, categories = categories, judges = judges)
    else:
        flash("You are not an admin!")
        return render_template("index.html")

@app.route("/get_categories", methods = ['GET', 'POST'])
@login_required
def get_categories():
    tournament_id = request.args.get("tournament", type=int)
    categories = Category.query.filter_by(tournament_id=tournament_id).all()
    return render_template("category_options.html", categories=categories)

@app.route("/admin/users", methods = ['GET', 'POST'])
@login_required
def users_admin():
    form = UserForm()
    users = Users.query.all()
    
    if request.method == "POST":
        flash("Form is validated!")  
        username = form.username.data
        real_name = form.real_name.data
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        add_instance(Users,username = username, real_name = real_name, password_hash = hashed_pw, user_type = 'User')
        return redirect(url_for('users_admin'))
            
    if current_user.user_type == "admin" or "superadmin":
        return render_template("users_admin.html", form = form, users = users)
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
    categories = Category.query.all()
    return render_template('provas.html', tournaments=tournaments, categories=categories)


@app.route("/poomsae_athlete", methods = ['GET']) 
def poomsaes_athlete():
    return render_template('poomsae-athlete.html')


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


@app.route("/admin/users/delete/<int:id>", methods = ['GET', 'POST'])
@login_required
def delete_user(id):
    user = Users.query.get_or_404(id)

    if user != 0:
        delete_instance(user, id)
        flash('User deleted!')
        return redirect(url_for('users_admin'))

    return render_template('dashboard_admin.html')


@app.route("/admin/tournaments/delete/<int:tournament_id>", methods = ['GET', 'POST'])
@login_required
def delete_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament != 0:
        delete_instance(tournament, tournament.id)
        flash('Tournament deleted!')
        return redirect(url_for('tournaments_admin'))

    return render_template('dashboard_admin.html')

@app.route("/admin/athlete/delete/<int:athlete_id>", methods = ['GET', 'POST'])
@login_required
def delete_athlete(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)

    if athlete != 0:
        athlete.list_of_poomsaes.clear()
        commit_changes()
        delete_instance(athlete, athlete.id)
        flash('Athlete deleted!')
        return redirect(url_for('athletes_admin'))

    return render_template('athletes_admin.html')

@app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)

    if category != 0:
        delete_instance(category, category.id)
        return redirect(url_for('categories_admin'))

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


@app.route("/provas/<int:id>", methods = ['GET', 'POST'])
def provas_by_id(id):
    prova = Category.query.get_or_404(id)
    athletes = prova.list_of_athletes
    
    for athlete in athletes:
        strength_and_velocity = 0
        rythm_and_coordenation = 0
        energy_expression = 0
        technical_component = 0
        poomsae_median = 0
        for poomsae in athlete.list_of_poomsaes:
            strength_and_velocity += poomsae.strength_and_velocity
            rythm_and_coordenation += poomsae.rythm_and_coordenation
            energy_expression += poomsae.energy_expression
            technical_component += poomsae.technical_component
        for poomsae in athlete.list_of_poomsaes:
            poomsae.strength_and_velocity = strength_and_velocity / len(athlete.list_of_poomsaes)
            poomsae.rythm_and_coordenation = rythm_and_coordenation / len(athlete.list_of_poomsaes)
            poomsae.energy_expression = energy_expression / len(athlete.list_of_poomsaes)
            poomsae.technical_component = round(technical_component / len(athlete.list_of_poomsaes),2)
            poomsae.presentation_component = round(poomsae.strength_and_velocity + poomsae.rythm_and_coordenation + poomsae.energy_expression,2)
            poomsae_median = round(poomsae.technical_component + poomsae.presentation_component,2)
        athlete.poomsae_median = poomsae_median

    sorted_athlete_list = sorted(athletes, key=lambda x: x.poomsae_median, reverse=True)
    for i, athlete in enumerate(sorted_athlete_list):
        athlete.rank = i + 1
    if prova != 0:
        return render_template('prova_by_id.html', prova=prova, athletes= athletes)


@app.route("/update_tournament/<int:id>", methods = ['GET', 'POST'])
def update_tournament(id):
    form = TournamentForm()
    tournaments = Tournament.query.all()
    tournament_to_update = Tournament.query.get_or_404(id)
    if request.method == 'POST':
        tournament_to_update.name = request.form['name']
        try:
            commit_changes()
            flash('Tornament Updated Sucessfully')
            return render_template("update_tournament.html", form=form, tournament_to_update = tournament_to_update)
        except:
            flash('Error!')
            return render_template("update_tournament.html", form=form, tournament_to_update = tournament_to_update)
    else:
        return render_template("update_tournament.html", form=form, tournament_to_update = tournament_to_update)


@app.route("/update_category/<int:id>", methods = ['GET', 'POST'])
def update_category(id):
    form = CategoryForm()
    category_to_update = Category.query.get_or_404(id)
    if request.method == 'POST':
        category_to_update.name = request.form['name']
        try:
            commit_changes()
            flash('Category Updated Sucessfully')
            return render_template("update_category.html", form=form, category_to_update = category_to_update)
        except:
            flash('Error!')
            return render_template("update_category.html", form=form, category_to_update = category_to_update)
    else:
        return render_template("update_category.html", form=form, category_to_update = category_to_update)
    

@app.route("/update_athlete/<int:id>", methods = ['GET', 'POST'])
def update_athlete(id):
    form = AthleteForm()
    athlete_to_update = Athlete.query.get_or_404(id)
    if request.method == 'POST':
        athlete_to_update.name = request.form['name']
        try:
            commit_changes()
            flash('Athlete Updated Sucessfully')
            return render_template("update_athlete.html", form=form, athlete_to_update = athlete_to_update)
        except:
            flash('Error!')
            return render_template("update_athlete.html", form=form, athlete_to_update = athlete_to_update)
    else:
        return render_template("update_athlete.html", form=form, athlete_to_update = athlete_to_update)





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
            return render_template("update_user.html", form=form, user_to_update = user_to_update, id = id)
        user_to_update.password_hash = generate_password_hash(user_to_update.password_hash,"sha256") 
        user_to_update.password_hash2 = generate_password_hash(user_to_update.password_hash,"sha256") 
        try:
            commit_changes()
            flash("User Updated sucessfully")
            return render_template("update_user.html", form=form, user_to_update = user_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update_user.html", form=form, user_to_update = user_to_update, id = id)
    else:
        return render_template("update_user.html", form=form, user_to_update = user_to_update, id = id)
    


@app.route("/update_judge/<int:id>", methods = ['GET', 'POST'])
def update_judge(id):
    form = JudgeForm()
    judge_to_update = Judge.query.get_or_404(id)
    if request.method == "POST":
        print(request.form)
        judge_to_update.username = request.form['username']
        judge_to_update.real_name = request.form['real_name']
        judge_to_update.password_hash = request.form['password_hash']   
        judge_to_update.password_hash2 = request.form['password_hash2']
        judge_to_update.type_of_jury = request.form['type_of_jury'] 
        if(judge_to_update.password_hash != judge_to_update.password_hash2) :
            flash("Passwords não são iguais!")
            return render_template("update.html", form=form, judge_to_update = judge_to_update, id = id)
        judge_to_update.password_hash = generate_password_hash(judge_to_update.password_hash,"sha256") 
        judge_to_update.password_hash2 = generate_password_hash(judge_to_update.password_hash,"sha256") 
        try:
            commit_changes()
            flash("User Updated sucessfully")
            return render_template("update_judge.html", form=form, judge_to_update = judge_to_update, id = id)
        except:
            flash("Error!")
            return render_template("update_judge.html", form=form, judge_to_update = judge_to_update, id = id)
    else:
        return render_template("update_judge.html", form=form, judge_to_update = judge_to_update, id = id)





    
@app.route('/delete_judge/<int:id>')
def delete_judge(id):
    judge_to_delete = Judge.query.get_or_404(id)
    user_to_delete = Users.query.get_or_404(id)
    try:
        delete_instance(judge_to_delete, id)
        delete_instance(user_to_delete, id)
        flash("Judge deleted sucessfully!")
        return redirect(url_for('judges_admin'))
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
            add_instance(Tournament, name = form.category_name.data + "tournament")
        
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

@app.route('/lobby', methods=['GET', 'POST'])
@login_required
def lobby():
    categories = Category.query.all()
    tournaments = Tournament.query.all()
    judges = Judge.query.all()
    if tournaments is None:
        abort(404)

    return render_template("lobby.html", tournaments=tournaments, categories = categories, current_user = current_user, judges = judges)

@app.route('/judge_lobby/<int:tournament_id>')
@login_required
def judge_lobby(tournament_id):
    active_tournament = Tournament.query.get(tournament_id)
    if active_tournament is None:
        abort(404)

    if current_user.user_type == 'admin':
        return redirect(url_for('lobby', tournament_id=tournament_id))

    return render_template("judge_lobby.html", tournament=active_tournament)




def generate_unique_poomsae_name(athlete_name):
    unique_id = uuid.uuid4().hex[:6]  
    return f"{athlete_name}Poomsae{unique_id}"

submitted_evaluations = {}
@app.route('/<int:judge_id>/juri_interface', methods=['GET', 'POST'])
@login_required
def judge_interface(judge_id):
    
    if request.method == 'GET':
        if current_user.user_type not in ['admin', 'judge', 'superadmin']:
            abort(403)

        tournament_id = request.args.get('tournament_id')
        category_id = request.args.get('category_id')
        
        active_athlete = Athlete.query.filter_by(category_id=category_id, tournament_id=tournament_id).first()
        if active_athlete is not None:
            active_athlete.active = True
            commit_changes()
        

        active_tournament = Tournament.query.get(tournament_id)
        if not active_tournament or not active_tournament.active:
            return redirect(url_for('lobby'))

        active_category = Category.query.get(category_id)
        if not active_category or active_category.tournament_id != active_tournament.id:
            abort(404)
            
        session['tournament_active'] = True
        if not session.get('tournament_active', False):
            return redirect(url_for('lobby'))

    if request.method == 'POST':
        data = request.get_json()
        strength_and_velocity = data.get('strength_and_velocity')
        rythm_and_coordenation = data.get('rhythm_and_coordination')
        energy_expression = data.get('energy_expression')
        technical_component = data.get('technical_component')
        athlete = data.get('name')
        athlete_id = data.get('athlete_id')
        tournament_id = data.get('tournament_id')
        category_id = data.get('category_id')
        judge_id = current_user.id
        poomsae_name = generate_unique_poomsae_name(athlete)

        
        add_instance(Poomsae,name = poomsae_name,
        tournament_id = tournament_id,
        strength_and_velocity=strength_and_velocity,
        rythm_and_coordenation=rythm_and_coordenation,
        energy_expression=energy_expression,
        technical_component=technical_component)
        
        results = Poomsae.query.filter_by(name = poomsae_name).first()

        active_athlete = Athlete.query.filter_by(id=athlete_id).first()
        active_athlete.list_of_poomsaes.append(results)
        commit_changes()
        
        active_category = Category.query.filter_by(id = category_id).first()
        active_tournament = Tournament.query.filter_by(id = tournament_id).first()
        

        active_athlete.active = False
        if Athlete.query.filter((Athlete.id > active_athlete.id) & (Athlete.category_id == category_id) & (Athlete.tournament_id == tournament_id)).first() == None:

            response_data = {
            'next_athlete_name': None,
            'tournament_name': active_tournament.name,
            'tournamentIdElement' : active_tournament.id,
            'categoryIdElement' : active_category.id,
            }
            return response_data
        
        next_active_athlete = Athlete.query.filter((Athlete.id > active_athlete.id) & (Athlete.category_id == category_id) & (Athlete.tournament_id == tournament_id)).first()
        if next_active_athlete is not None:
            next_active_athlete.active = True
   
            commit_changes()
            response_data = {
            'next_athlete_name': next_active_athlete.name if next_active_athlete else None,
            'tournament_name': active_tournament.name,
            'tournamentIdElement' : active_tournament.id,
            'categoryIdElement' : active_category.id,
            'athlete_id' : next_active_athlete.id
            }
            return jsonify(response_data)

        

    return render_template("judge_interface.html", active_athlete=active_athlete, active_tournament=active_tournament, active_category=active_category,current_user = current_user)


########################################################################################################


class UserType(Enum):
    user = 'user'
    admin = 'admin'
    



     

class UserForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    real_name= StringField("Real Name: ", validators=[DataRequired()])
    password_hash = PasswordField('Password:', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")


class JudgeForm(UserForm):
    type_of_jury = SelectField('Type of Jury', choices=[('normal', 'Normal'), ('major', 'Major')], default='normal')
    tournament = QuerySelectField('Tournament', query_factory=lambda: Tournament.query.all(), allow_blank = True, get_label = "name")
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), allow_blank = True, get_label = "name")
    submit = SubmitField('Submit')

class AthleteForm(UserForm):
    name = StringField("Username", validators=[DataRequired()])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), allow_blank = True, get_label ="name")
    tournament = QuerySelectField('Tournament', query_factory=lambda: Tournament.query.all(), allow_blank = True, get_label ="name")
    submit = SubmitField("Create Athlete")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
    
class AdminForm(UserForm):
    type_of_admin = SelectField('Type of Admin', choices = [('admin', 'Admin' , ('superadmin', 'Superadmin'))], default = 'admin')
    
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    tournament = QuerySelectField('Tournament', query_factory=lambda: Tournament.query.all(), allow_blank = True, get_label ="name")
    submit = SubmitField('Create Category')

class TournamentForm(FlaskForm):
    submit = SubmitField('Criar Troneio')
    name = StringField('Nome do Torneio: ', validators=[DataRequired()])
