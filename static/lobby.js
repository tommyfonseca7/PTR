document.addEventListener('DOMContentLoaded', function () {
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Connected to SocketIO');
        socket.emit('join_lobby');
    });

    socket.on('judge_joined', function (data) {
        const numJudges = data.num_judges;
        document.getElementById('status').textContent = `Judges in lobby: ${numJudges}`;
        if (numJudges >= 2) {
            window.location.href = '/judge_interface'; // Redirect to judge_interface.html when 2 or more judges join
        }
    });

    socket.on('judge_left', function (data) {
        const numJudges = data.num_judges;
        document.getElementById('status').textContent = `Judges in lobby: ${numJudges}`;
    });

    socket.on('disconnect', function () {
        console.log('Disconnected from SocketIO');
    });

});