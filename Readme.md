# Real-Time Messaging Platform

A production style real time messaging web application built from scratch using FastAPI, async SQLAlchemy, PostgreSQL, JWT authentication and WebSockets.

This project demonstrates backend system design, real-time distributed communication, authentication architecture and scalable API-driven application structure.


## 🚀 Overview

The application allows authenticated users to:

- Register and log in using JWT based authentication
- Create or access direct conversations
- Send and receive messages in real time using WebSockets
- Track unread messages
- Display typing indicators
- Persist conversation history in PostgreSQL

The system is designed with production oriented architecture principles including async database access, separation of concerns and stateless authentication.


## 🏗️ Architecture

### High-Level Design

Browser (Frontend - Vanilla JS)
|
| REST API (Auth, Conversations, Messages)
v
FastAPI Backend (Async)
|
| Async SQLAlchemy ORM
v
PostgreSQL
|
| WebSocket Layer
v
Real-Time Broadcast per Conversation

### Architecture Diagram

![Architecture Diagram](architecture.png)


## 🔐 Authentication

- JWT based stateless authentication
- Password hashing via Argon2
- Protected REST and WebSocket endpoints
- `/auth/me` endpoint for identity verification

Stateless authentication enables horizontal scaling and API first system design.


## ⚡ Real-Time Communication

WebSockets are used to maintain persistent connections per conversation.

Each conversation maintains its own broadcast group:

```python
active_connections: Dict[int, List[WebSocket]]

Message Flow:
	1.	Client sends message via WebSocket.
	2.	Message is persisted to PostgreSQL.
	3.	Backend broadcasts to all connected participants.

Typing indicators are broadcast only events and are not persisted.

⸻

🗄️ Database Schema

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

Unread tracking is implemented using last_read_message_id to avoid expensive full-table scans.

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
	•	WS /ws/{conversation_id}

⸻

📈 Scalability Considerations
	•	Stateless JWT authentication
	•	Async database access for concurrency
	•	Conversation scoped WebSocket groups
	•	Message persistence before broadcast
	•	Clear separation between routing, models, and business logic

In a multi instance deployment, the WebSocket layer could be extended using a message broker (e.g., Redis Pub/Sub) to synchronize events across instances.

⸻

🔎 Production Readiness

The architecture supports:
	•	Centralized logging
	•	Structured error handling
	•	Modular route organization
	•	Testable API endpoints
	•	Containerized deployment

⸻

🛠️ Running Locally

Backend

cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend

Serve chat.html using a static server (e.g., Live Server).