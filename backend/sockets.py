from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit,  join_room, leave_room
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