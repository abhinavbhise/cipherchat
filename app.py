from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

users = {}

@app.route('/')
def index():
    return render_template('index.html')

# 🔥 User joins
@socketio.on('join')
def handle_join(data):
    username = data['username']
    users[request.sid] = username

    socketio.emit(
        'message',
        f"{username} joined the chat!",
        broadcast=True
    )

# 💬 Message handler
@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = users.get(request.sid, "Unknown")

    # 🔐 Private message
    if msg.startswith("@"):
        try:
            target, message = msg.split(" ", 1)
            target_username = target[1:]

            for sid, user in users.items():
                if user == target_username:
                    socketio.emit(
                        'message',
                        f"(Private) {username}: {message}",
                        to=sid
                    )
                    return
        except:
            pass

    # 🌍 Public message
    socketio.emit(
        'message',
        f"{username}: {msg}",
        broadcast=True
    )

# ❌ User leaves
@socketio.on('disconnect')
def handle_disconnect():
    username = users.get(request.sid, "User")

    if request.sid in users:
        del users[request.sid]

    socketio.emit(
        'message',
        f"{username} left the chat",
        broadcast=True
    )

# 🚀 Run app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
