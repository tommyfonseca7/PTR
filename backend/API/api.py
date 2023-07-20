from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.models import db
from backend.models import Users, Judge, Category, Tournament, Athlete, Poomsae





user_api = Blueprint('routes_user_api', __name__)



@user_api.route('/api/create_category', methods=['POST'])
def create_category_api():
    category_name = request.json.get('name')

    if not category_name:
        return jsonify({'error': 'Category name is required.'}), 400

    category = Category(name=category_name)

    try:
        db.session.add(category)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    

    return jsonify({'message': 'Category created successfully.'}), 201


@user_api.route('/api/athletes', methods=['POST'])
def create_athlete():
    data = request.get_json()
    name = data.get('name')
    category_type = data.get('category_id')
    active = data.get('active')
    tournament_id = data.get('tournament_id')

    # Create Athlete
    athlete = Athlete(name = name, category_id=category_type, active=active, tournament_id=tournament_id)
    db.session.add(athlete)
    db.session.commit()

    return jsonify({'message': 'Athlete created successfully.', 'athlete_id': athlete.id}), 201

@user_api.route('/api/create_tournament', methods=['POST'])
def create_tournament_api():
    data = request.get_json()
    name = data.get('name')
    tournament = Tournament(name=name)
    db.session.add(tournament)
    db.session.commit()
    
    judges_data = data.get('judges', [])
    if judges_data:
        for judge_data in judges_data:
            judge_name = judge_data.get('name')
            judge = Judge(name=judge_name)
            tournament.list_of_judges.append(judge)
            db.session.add(judge)

    # Create Athletes (if provided)
    athletes_data = data.get('athletes', [])
    if athletes_data:
        for athlete_data in athletes_data:
            athlete_name = athlete_data.get('name')
            athlete = Athlete(name=athlete_name)
            tournament.list_of_athletes.append(athlete)
            db.session.add(athlete)
            
    return jsonify({'message': 'Tournament created successfully.'}), 201

@user_api.route('/api/create_judge', methods=['POST'])
def create_judge_api():
    data = request.get_json()
    username = data.get('username')
    real_name = data.get('real_name')
    password_hash = generate_password_hash(data.get('password'))
    user_type = data.get('user_type')
    date_added = datetime.utcnow()
    category_name = data.get('category_name')
    tournament_id = data.get('tournament_id')
    type_of_jury = data.get('type_of_jury', 'normal')
    category_name = Category(name = category_name)
    user = Users(username=username, real_name=real_name, password_hash=password_hash, user_type = user_type, date_added = date_added)
    judge = Judge(user=user, category_name=category_name.name, tournament_id=tournament_id, type_of_jury=type_of_jury)

    db.session.add(user)
    db.session.add(judge)
    db.session.commit()

    return jsonify({
        'id': judge.id,
        'username': user.username,
        'email': user.password_hash,
        'category_name': judge.category_name,
        'tournament_id': judge.tournament_id,
        'type_of_jury': judge.type_of_jury
    }), 201

@user_api.route('/api/create_user', methods=['POST'])
def create_user_api():
    data = request.get_json()
    username = data.get('username')
    real_name = data.get('real_name')
    password_hash = generate_password_hash(data.get('password'))
    user_type = data.get('user_type')
    date_added = datetime.utcnow()

    # create a new user instance

    new_user = Users(username=username,real_name = real_name, password_hash=password_hash, user_type=user_type, date_added=date_added)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!'})

@user_api.route("/api/update_user/<int:id>", methods=['POST'])
def update_user_api(id):
    data = request.get_json()
    username = data.get('username')
    password_hash = generate_password_hash(data.get('password_hash'), "sha256")
    user_perms = data.get('user_perms')
    user_to_update = Users.query.get_or_404(id)

    user_to_update.username = username
    user_to_update.password_hash = password_hash
    user_to_update.user_perms = user_perms
    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except:
        return jsonify({'error': 'Failed to update user'})
    
@user_api.route("/api/update_judge/<int:id>", methods=['POST'])
def update_judge_api(id):
    data = request.get_json()
    username = data.get('username')
    password_hash = generate_password_hash(data.get('password_hash'), "sha256")
    user_perms = data.get('user_perms')
    user_to_update = Users.query.get_or_404(id)

    user_to_update.username = username
    user_to_update.password_hash = password_hash
    user_to_update.user_perms = user_perms
    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except:
        return jsonify({'error': 'Failed to update user'})
    
@user_api.route("/api/update_tournament/<int:id>", methods=['POST'])
def update_tournament_api(id):
    data = request.get_json()
    tournament_name = data.get('tournament_name')
    athlete_ids = data.get('athlete_ids')
    judge_ids = data.get('judge_ids')

    tournament_to_update = Tournament.query.get_or_404(id)

    tournament_to_update.name = tournament_name

    # Update athletes
    if athlete_ids:
        tournament_to_update.list_of_athletes = Athlete.query.filter(Athlete.id.in_(athlete_ids)).all()

    # Update judges
    if judge_ids:
        tournament_to_update.list_of_judges = Judge.query.filter(Judge.id.in_(judge_ids)).all()

    try:
        db.session.commit()
        return jsonify({'message': 'Tournament updated successfully'})
    except:
        return jsonify({'error': 'Failed to update tournament'})
    
    
@user_api.route('/api/get_users', methods=['GET'])
def get_users():
    users = Users.query.all()
    user_list = [user.__dict__ for user in users]
    for user in user_list:
        user.pop('_sa_instance_state')
    return jsonify(user_list), 200

@user_api.route("/api/get_tournaments", methods=["GET"])
def get_tournaments():
    tournaments = Tournament.query.all()
    tournament_list = []
    for tournament in tournaments:
        tournament_data = {
            'id': tournament.id,
            'name': tournament.name,
            'active': tournament.active,
            'list_of_judges': [judge.id for judge in tournament.list_of_judges],
            'list_of_athletes': [athlete.id for athlete in tournament.list_of_athletes.all()]
        }
        tournament_list.append(tournament_data)
    return jsonify(tournament_list)

@user_api.route("/api/get_judges", methods=["GET"])
def get_judges():
    judges = Judge.query.all()
    judges_list = [judge.__dict__ for judge in judges]
    for judge in judges_list:
        judge.pop('_sa_instance_state')
    return jsonify(judges_list)


@user_api.route("/api/get_category", methods=["GET"])
def get_category():
    categorys = Category.query.all()
    category_list = [category.__dict__ for category in categorys]
    for category in category_list:
        category.pop('_sa_instance_state')
    return jsonify(category_list)

@user_api.route('/api/get_athletes', methods=['GET'])
def get_athletes():
    athletes = Athlete.query.all()
    athlete_list = []

    for athlete in athletes:
        athlete_data = {
            'id': athlete.id,
            'name': athlete.name,
            'active': athlete.active,
            'category_id' : athlete.category_id,
            'tournament_id': athlete.tournament_id,
            'list_of_poomsaes': [poomsae.id for poomsae in athlete.list_of_poomsaes]
        }
        athlete_list.append(athlete_data)

    return jsonify(athlete_list)


@user_api.route('/api/update_athlete/<int:id>', methods=['POST'])
def update_athlete(id):
    data = request.get_json()
    name = data.get('name')
    category_type = data.get('category_type')
    active = data.get('active')
    list_of_poomsaes = data.get('list_of_poomsaes')

    athlete = Athlete.query.get_or_404(id)
    print(name)
    athlete.name = name
    athlete.category_type = category_type
    athlete.active = active
    # Update the list of poomsaes if provided
    if list_of_poomsaes:
        athlete.list_of_poomsaes = Poomsae.query.filter(Poomsae.id.in_(list_of_poomsaes)).all()
    db.session.commit()
    return jsonify({'message': 'Athlete updated successfully'})
  
@user_api.route('/api/get_poomsae', methods=['GET'])
def get_poomsae():
    poomsae_list = Poomsae.query.all()
    poomsae_data = []
    
    for poomsae in poomsae_list:
        poomsae_dict = {
            'id': poomsae.id,
            'name': poomsae.name,
            'strength_and_velocity': poomsae.strength_and_velocity,
            'rythm_and_coordenation': poomsae.rythm_and_coordenation,
            'energy_expression': poomsae.energy_expression,
            'technical_component': poomsae.technical_component,
            'tournament_id': poomsae.tournament_id,
            'date_added': poomsae.date_added.strftime("%Y-%m-%d %H:%M:%S")
        }
        poomsae_data.append(poomsae_dict)
    
    return jsonify(poomsae_data)