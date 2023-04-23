from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask import Blueprint
from datetime import datetime
from app import db
from models import Users, Judge, Category, Tournament





user_api = Blueprint('routes_user_api', __name__)


@user_api.route('/api/create_category', methods=['POST'])
def create_category():
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

@user_api.route('/api/create_tournament', methods=['POST'])
def create_tournament():
    data = request.get_json()
    name = data.get('name')
    tournament = Tournament(name=name)
    db.session.add(tournament)
    db.session.commit()
    return jsonify({'message': 'Tournament created successfully.'}), 201

@user_api.route('/api/create_judge', methods=['POST'])
def create_judge2():
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
def create_user2():
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
def update_user2(id):
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
    tournament_list = [tournament.__dict__ for tournament in tournaments]
    for tournament in tournament_list:
        tournament.pop('_sa_instance_state')
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