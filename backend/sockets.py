from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit,  join_room, leave_room
from models.backend import *
from models.databse import *
from models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

MAX_JUDGES = 6
connected_judges = 0
form_submitted_count = 0
active_user_id = None
current_tournament_id = None
current_athlete_index = 0
evaluation_time_limit = 180  #

@app.route('/')
def index():
    return render_template('lobby.html')

@socketio.on('connect')
def handle_connect():
    global connected_judges
    connected_judges += 1

    # Notify the client about the number of connected judges
    emit('connected judges', connected_judges, broadcast=True)

    # Check if the required number of judges has connected
    if connected_judges == MAX_JUDGES:
        emit('lobby ready', broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global connected_judges
    connected_judges -= 1

    # Notify all clients about the updated number of connected judges
    emit('connected judges', connected_judges, broadcast=True)
    
    
@app.route('/evaluation/<int:tournament_id>/<int:athlete_id>')
def evaluation(tournament_id, athlete_id):
    # Check if the judge is assigned to the provided tournament_id
    judge = Judge.query.filter_by(id=current_judge.id).first()
    assigned_tournament_ids = [t.id for t in judge.tournaments]
    if tournament_id not in assigned_tournament_ids:
        # Handle unauthorized access or redirect to an error page
        return "Unauthorized", 401

    # Get the tournament and athlete from the database based on the tournament_id and athlete_id
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    athlete = Athlete.query.filter_by(id=athlete_id, tournament_id=tournament_id).first()

    if not athlete:
        # Handle invalid athlete_id or redirect to an error page
        return "Invalid athlete ID", 404

    return render_template('evaluation.html', active_athlete=athlete, tournament=tournament)


@socketio.on('join_evaluation')
def handle_join_evaluation(data):
    global active_user_id, current_tournament_id, current_athlete_index

    current_tournament_id = data['tournament_id']
    tournament = Tournament.query.filter_by(id=current_tournament_id).first()
    athletes = tournament.list_of_athletes.all()

    if current_athlete_index < len(athletes):
        active_user_id = athletes[current_athlete_index].id
        athletes[current_athlete_index].active = True
        db.session.commit()

        join_room(str(active_user_id))
        emit('start_evaluation', {'time_limit': evaluation_time_limit}, room=request.sid)
    else:
        # Handle the case when there are no more athletes to evaluate in the current tournament
        emit('no_more_athletes', room=request.sid)

@socketio.on('submit_evaluation')
def handle_submit_evaluation(data):
    global active_user_id, current_athlete_index

    user = Athlete.query.filter_by(id=active_user_id).first()
    if user:
        user.evaluation = data['evaluation']  # Assuming you have a property 'evaluation' in the Athlete class
        db.session.commit()

        leave_room(str(active_user_id))
        active_user_id = None

    current_athlete_index += 1  # Move to the next athlete
    handle_join_evaluation({'tournament_id': current_tournament_id})  # Call the function to handle next athlete
    
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
