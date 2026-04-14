from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected:", request.sid)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    users[request.sid] = username

    socketio.emit('message', f"{username} joined the chat!")

@socketio.on('message')
def handle_message(data):
    print("Received:", data)

    msg = data.get('msg')
    username = users.get(request.sid, "Unknown")

    if not msg:
        return

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

    socketio.emit('message', f"{username}: {msg}")

@socketio.on('disconnect')
def handle_disconnect():
    username = users.get(request.sid, "User")

    if request.sid in users:
        del users[request.sid]

    socketio.emit('message', f"{username} left the chat")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
