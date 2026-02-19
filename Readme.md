<h1 align="center">🍻 Brewverse v1.0.0</h1>

<p align="center">
Production-ready real-time messaging platform built with FastAPI, WebSockets, PostgreSQL & JWT
</p>

<p align="center">
  <a href="https://brewverse.vercel.app"><strong>🚀 Live Application</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" />
  <img src="https://img.shields.io/badge/backend-FastAPI-green" />
  <img src="https://img.shields.io/badge/database-PostgreSQL-blue" />
  <img src="https://img.shields.io/badge/realtime-WebSockets-orange" />
  <img src="https://img.shields.io/badge/auth-JWT-red" />
</p>

---

## 🚀 Overview

Brewverse is a production-grade real-time messaging platform built from scratch using:

- **FastAPI (async backend)**
- **Async SQLAlchemy**
- **PostgreSQL (Supabase)**
- **JWT authentication**
- **WebSockets (dual socket architecture)**
- **Vanilla JavaScript frontend**

Version **1.0.0** introduces stable conversation ordering, real-time notification sockets, and production-ready unread tracking.

---

## ✨ Features

- 🔐 JWT-based stateless authentication  
- 💬 Real-time messaging via WebSockets  
- 🔔 Dedicated notification WebSocket channel  
- 📊 Intelligent unread message tracking  
- 📈 Automatic conversation reordering (database-driven)  
- ⌨️ Typing indicators  
- 📱 Mobile responsive UI  
- 🌐 Production deployment (Vercel + Render + Supabase)  

---

## 🔔 Real-Time Notification System (v1.0.0)

Brewverse includes a dedicated notification socket:

(WS /ws/notifications)

### What It Handles

- Live unread count updates  
- Sidebar refresh without reload  
- Browser tab title updates  
- Custom in-app toast notifications  
- Cross-device synchronization  

Unread tracking is handled using `last_read_message_id` — avoiding expensive full-table scans.

---

## 📊 Intelligent Conversation Ordering

Conversations are ordered using an `updated_at` timestamp.

Whenever a new message is sent:

1. Message is persisted
2. `updated_at` is updated in the `conversations` table
3. Conversations automatically reorder across all clients

Ordering logic:

```python
.order_by(Conversation.updated_at.desc())
```

No frontend hacks. Fully database-driven.

⸻

🏗 Architecture

High-Level Design

Browser (Vanilla JS)
        │
        ├── REST API (Auth, Conversations, Messages)
        ▼
FastAPI Backend (Async)
        │
        ├── Async SQLAlchemy ORM
        ▼
PostgreSQL (Supabase)
        │
        ├── WebSocket Layer
        ▼
Real-Time Broadcast per Conversation


⸻

🧩 Architecture Diagram

<p align="center">
  <img src="arch.png" width="750"/>
</p>



⸻

⚡ Real-Time Message Flow

Each conversation maintains its own WebSocket broadcast group:

active_connections: Dict[int, List[WebSocket]]

Message Lifecycle
	1.	Client sends message via WebSocket
	2.	Message is saved to PostgreSQL
	3.	Conversation updated_at is updated
	4.	Message broadcast to all active participants
	5.	Notification socket updates unread state

Typing indicators are broadcast-only events and are not persisted.

⸻

🔐 Authentication
	•	Stateless JWT authentication
	•	Password hashing via Argon2
	•	Protected REST & WebSocket endpoints
	•	/auth/me identity verification endpoint

This allows horizontal scalability and clean API-first architecture.

⸻

🗄 Database Schema

Users
	•	id
	•	email (unique)
	•	username (unique)
	•	display_name
	•	password_hash
	•	created_at

Conversations
	•	id
	•	is_group
	•	created_at
	•	updated_at

Conversation Participants
	•	conversation_id
	•	user_id
	•	last_read_message_id
	•	role

Messages
	•	id
	•	conversation_id
	•	sender_id
	•	content
	•	created_at

⸻

📡 API Endpoints

Authentication
	•	POST /auth/signup
	•	POST /auth/login
	•	GET /auth/me

Conversations
	•	GET /conversations/
	•	POST /conversations/direct/{username}
	•	POST /conversations/{conversation_id}/read

Messages
	•	GET /messages/{conversation_id}
	•	POST /messages

WebSocket
	•	WS /ws/chat/{conversation_id}
	•	WS /ws/notifications

⸻

📈 Scalability Considerations
	•	Stateless JWT authentication
	•	Async DB access for concurrency
	•	Conversation-scoped WebSocket groups
	•	Message persistence before broadcast
	•	Clean separation of routing, models, and business logic

Future horizontal scaling can integrate Redis Pub/Sub for multi-instance synchronization.

⸻

🧪 Testing

Tests use pytest with ASGI transport.

Run locally:

cd Backend
python -m pytest

CI pipeline runs automatically on every push to main.

⸻

🐳 Docker Support

Build:

cd Backend
docker build -t brewverse_backend .

Run:

docker run -p 8000:8000 brewverse_backend


⸻

🛠 Running Locally

Backend

cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000


⸻

Frontend

cd Frontend
python3 -m http.server 5500

Open:

http://localhost:5500


⸻

📌 Version

Current Stable Release: v1.0.0

⸻

👨‍💻 Author

Prajjwal
Full-stack backend-focused developer
Built from scratch as a production-style system.