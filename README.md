# cipherchat
# 🔐 CipherChat

CipherChat is a real-time web-based chat application with user-level encryption, built using Flask and Socket.IO. It allows multiple users to communicate instantly across devices with a clean modern UI.

---

## 🚀 Features

- 🌐 Real-time messaging (Socket.IO)
- 👥 Multi-user chat system
- 🔐 Unique encryption key for each user
- 💬 Private messaging using @username
- 🎨 Modern dark UI with chat bubbles
- 📱 Cross-device compatibility
- ⚡ Live deployment (Render)

---

## 🧠 How It Works

- Each user joins with a username
- A unique encryption key is generated for every user
- Messages are encrypted using a simple XOR-based algorithm
- Messages are broadcasted to all connected clients in real-time

---

## 🛠️ Tech Stack

- Backend: Python (Flask)
- Realtime: Flask-SocketIO
- Frontend: HTML, CSS, JavaScript
- Deployment: Render

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/cipherchat.git
cd cipherchat
pip install -r requirements.txt
python app.py