from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

MAX_JUDGES = 6
connected_judges = 0
form_submitted_count = 0

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

@socketio.on('form submitted')
def handle_form_submission():
    global form_submitted_count
    form_submitted_count += 1

    # Notify all clients about the submitted form
    emit('form submitted', form_submitted_count, broadcast=True)

    # Check if all judges have submitted the form
    if form_submitted_count == MAX_JUDGES:
        emit('all forms submitted', broadcast=True)
        form_submitted_count = 0  # Reset the form submitted count for the next round

if __name__ == '__main__':
    socketio.run(app)