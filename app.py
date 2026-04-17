import os
import random
import string
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cse_project_secret_123'

# Using gevent async_mode as requested for live deployment
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

active_users = {}
user_keys = {}

def xor_cipher(text, key):
    return "".join(chr(ord(text[i]) ^ ord(key[i % len(key)])) for i in range(len(text)))

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    active_users[request.sid] = username
    random_key = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    user_keys[username] = random_key
    socketio.emit('server_message', {'msg': f"Welcome {username}! Your encryption key is: {random_key}", 'key': random_key}, to=request.sid)
    socketio.emit('server_message', {'msg': f"{username} has joined the chat."}, include_self=False)

@socketio.on('chat_message')
def handle_chat(data):
    session_id = request.sid
    if session_id in active_users:
        sender_name = active_users[session_id]
        sender_key = user_keys[sender_name]
        encrypted_msg = xor_cipher(data['msg'], sender_key)
        socketio.emit('chat_message', {'sender': sender_name, 'text': encrypted_msg})

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        username = active_users.pop(request.sid)
        socketio.emit('server_message', {'msg': f"{username} left the chat."})

if __name__ == '__main__':
    # Render requires dynamic port binding
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
