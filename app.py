from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    users[request.sid] = username
    send(f"{username} joined the chat!", broadcast=True)

@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = users.get(request.sid, "Unknown")

    if msg.startswith("@"):
        try:
            target, message = msg.split(" ", 1)
            target = target[1:]

            for sid, user in users.items():
                if user == target:
                    socketio.emit('message', f"(Private) {username}: {message}", to=sid)
                    return
        except:
            pass

    send(f"{username}: {msg}", broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = users.get(request.sid, "User")
    send(f"{username} left the chat", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
