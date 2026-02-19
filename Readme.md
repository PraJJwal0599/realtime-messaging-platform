🍻 Brewverse v1.0.0

Live Application:
👉 https://brewverse.vercel.app

Brewverse is a production-ready real-time messaging platform built with FastAPI, Async SQLAlchemy, PostgreSQL (Supabase), JWT authentication, and WebSockets.

Version 1.0.0 introduces stable real-time conversation ordering, a dedicated notification socket, and production-grade unread tracking.

⸻

🚀 Overview

The application allows authenticated users to:
	•	Register and log in using JWT-based authentication
	•	Create or access direct conversations
	•	Send and receive messages in real time using WebSockets
	•	Track unread messages dynamically
	•	Display typing indicators
	•	Persist conversation history in PostgreSQL
	•	Automatically reorder conversations based on last activity

The system follows production-oriented architecture principles including async database access, separation of concerns, stateless authentication, and database-driven state management.

⸻

🔔 Real-Time Notification System (v1.0.0)

Brewverse includes a dedicated WebSocket channel for real-time notifications.

Features
	•	Live unread count updates
	•	Sidebar refresh without reload
	•	Browser tab title updates on new messages
	•	Custom in-app toast notifications
	•	Conversation reordering based on last activity

Notification WebSocket Endpoint

WS /ws/notifications


⸻

📊 Intelligent Conversation Ordering (v1.0.0)

Conversations are ordered using an updated_at timestamp that updates whenever a new message is sent.

This ensures:
	•	Most recent conversation appears at the top
	•	Consistent ordering across refresh and devices
	•	No frontend reordering hacks
	•	Database-driven consistency

Ordering Logic

.order_by(Conversation.updated_at.desc())


⸻

🏗 Architecture

High-Level Design

Browser (Frontend - Vanilla JS)
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

Architecture Diagram


⸻

🔐 Authentication
	•	JWT-based stateless authentication
	•	Password hashing via Argon2
	•	Protected REST and WebSocket endpoints
	•	/auth/me endpoint for identity verification

Stateless authentication enables horizontal scaling and API-first system design.

⸻

⚡ Real-Time Communication

WebSockets maintain persistent connections per conversation.

Each conversation maintains its own broadcast group:

active_connections: Dict[int, List[WebSocket]]

Message Flow
	1.	Client sends message via WebSocket
	2.	Message is persisted to PostgreSQL
	3.	updated_at is updated in Conversations
	4.	Backend broadcasts to all connected participants
	5.	Notification socket updates unread counts

Typing indicators are broadcast-only events and are not persisted.

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
	•	WS /ws/chat/{conversation_id}
	•	WS /ws/notifications

⸻

📈 Scalability Considerations
	•	Stateless JWT authentication
	•	Async database access for concurrency
	•	Conversation-scoped WebSocket groups
	•	Message persistence before broadcast
	•	Clear separation between routing, models, and business logic

In a multi-instance deployment, the WebSocket layer can be extended using a message broker (e.g., Redis Pub/Sub) to synchronize events across instances.

⸻

🔎 Production Readiness

The architecture supports:
	•	Modular backend structure
	•	Environment-aware initialization
	•	Testable API endpoints
	•	CI-based validation pipeline
	•	Containerized deployment
	•	Real-time consistency across sessions

⸻

🧪 Testing

Tests are implemented using pytest and httpx with ASGI transport.

Run locally:

cd Backend
python -m pytest

A GitHub Actions workflow automatically runs tests on every push to main.

⸻

🐳 Docker Support

Build the image:

cd Backend
docker build -t brewverse_backend .

Run the container:

docker run -p 8000:8000 brewverse_backend

Then open:

http://127.0.0.1:8000


⸻

🛠 Running Locally

Backend

cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend runs at:

http://127.0.0.1:8000

Frontend

cd Frontend
python3 -m http.server 5500

Then open:

http://localhost:5500


⸻

📌 Version

Current stable release: v1.0.0

⸻