from flask import Flask, render_template, request
from flask_socketio import SocketIO
import random
import string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cse_project_secret_key'

# Setup SocketIO with gevent for production stability
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# Dictionaries to store active users and their encryption keys
active_users = {}
encryption_keys = {}

def xor_cipher(text, key):
    """
    Symmetric encryption using XOR bitwise operation.
    It loops over the text and applies the key repeatedly.
    """
    result = ""
    for i in range(len(text)):
        # Use modulo to loop the key if the text is longer than the key
        key_char = key[i % len(key)]
        # XOR the ASCII values and convert back to a character
        result += chr(ord(text[i]) ^ ord(key_char))
    return result

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('join_chat')
def handle_join(data):
    username = data['username']
    active_users[request.sid] = username
    
    # Generate a random 8-character key for this specific user
    characters = string.ascii_letters + string.digits
    user_key = ""
    for _ in range(8):
        user_key += random.choice(characters)
        
    encryption_keys[username] = user_key
    
    # Send the private key ONLY to the user who just joined
    socketio.emit('server_message', 
                  {'type': 'system', 'content': f"Welcome {username}. Your assigned XOR key is: {user_key}"}, 
                  room=request.sid)
    
    # Broadcast to everyone else that a user joined
    socketio.emit('server_message', 
                  {'type': 'system', 'content': f"{username} has joined the encrypted chat."}, 
                  include_self=False)

@socketio.on('send_message')
def handle_message(data):
    message_text = data.get('message')
    sender = active_users.get(request.sid, "Unknown User")
    
    if not message_text:
        return

    # Check if the user is trying to send a private message
    if message_text.startswith("@"):
        try:
            # Split the string into the target username and the actual message
            split_data = message_text[1:].split(" ", 1)
            target_user = split_data[0]
            actual_message = split_data[1]
            
            # Find the session ID of the target user
            target_sid = None
            for sid, name in active_users.items():
                if name == target_user:
                    target_sid = sid
                    break
            
            if target_sid:
                target_key = encryption_keys.get(target_user)
                encrypted_text = xor_cipher(actual_message, target_key)
                
                # Send to target
                socketio.emit('server_message', 
                              {'type': 'chat', 'sender': f"(Private from {sender})", 'content': encrypted_text}, 
                              room=target_sid)
                
                # Show confirmation to the sender (unencrypted so they can read what they sent)
                socketio.emit('server_message', 
                              {'type': 'chat', 'sender': f"(Private to {target_user})", 'content': actual_message, 'is_raw': True}, 
                              room=request.sid)
                return
        except IndexError:
            pass # Failsafe if the user types "@name" but forgets to type a message

    # If it's a normal broadcast message
    sender_key = encryption_keys.get(sender, "default")
    encrypted_text = xor_cipher(message_text, sender_key)
    
    socketio.emit('server_message', {'type': 'chat', 'sender': sender, 'content': encrypted_text})

@socketio.on('disconnect')
def handle_disconnect():
    username = active_users.get(request.sid)
    if username:
        del active_users[request.sid]
        socketio.emit('server_message', {'type': 'system', 'content': f"{username} disconnected."})

if __name__ == '__main__':
    # Render and Railway pass the port dynamically via environment variables
    # If it's running locally, it defaults to 5000
    port = int(os.environ.get("PORT", 5000))
    
    print("\n" + "="*50)
    print(f"🚀 SYSTEM ONLINE: CipherChat Server is running!")
    print(f"🌐 Access the application at: http://127.0.0.1:{port}")
    print("="*50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=port)
