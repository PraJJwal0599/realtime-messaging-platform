THIS_IS_THE_REAL_FILE = true;
console.log("APP JS VERSION 2");
let socket = null
const API_URL = "http://127.0.0.1:8000";

function scrollToBottomIfNear(box) {
    const threshold = 80; // pixels from bottom

    const isNearBottom =
        box.scrollHeight - box.scrollTop - box.clientHeight < threshold;

    if (isNearBottom) {
        box.scrollTop = box.scrollHeight;
    }
}

async function login(){
    console.log("login() called");

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(
        `${API_URL}/auth/login?email=${email}&password=${password}`,
        {method: "POST"}
    );

    if (!res.ok) {
        document.getElementById("error").innerText = "Login Failed";
        return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);

    // Try to get user_id safely
    try {
        const meRes = await fetch(`${API_URL}/auth/me`, {
            headers: {
                "Authorization": `Bearer ${data.access_token}`
            }
        });

        if (meRes.ok) {
            const meData = await meRes.json();
            localStorage.setItem("user_id", meData.id);
        }
    } catch (err) {
        console.log("Failed to fetch /auth/me:", err);
    }

    // Always redirect
    window.location.href = "chat.html";
}

async function loadChats() {
    console.log("Works loadchat");
    const token = localStorage.getItem("token");

    const res = await fetch(`${API_URL}/conversations/`,{
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const chats = await res.json();
    console.log("Chat response:", chats);

    const list = document.getElementById("chatList");
    list.innerHTML = "";

    chats.forEach (chat => {
        const li = document.createElement("li");
        li.innerText = `${chat.other_user.username} (${chat.unread_count})`;
        li.onclick = () => openChat(chat.conversation_id);
        list.appendChild(li);
    });
}

if (window.location.pathname.includes("chat.html")) {
    loadChats();
}

let currentConversationId = null;

async function openChat(conversationId) {
    console.log("Open chat called");
    currentConversationId = conversationId;
    const token = localStorage.getItem("token");

    await fetch(`${API_URL}/conversations/${conversationId}/read`,{
        method: "POST",
        headers: {"Authorization": `Bearer ${token}`}
    });

    const res = await fetch(`${API_URL}/messages/${conversationId}?limit=20`, {
        headers: {"Authorization": `Bearer ${token}`}
    });

    const messages = await res.json();
    console.log("Loaded messages:", messages);
    const box = document.getElementById("messages");
    box.innerHTML = "";

    const currentUserId = parseInt(localStorage.getItem("user_id"));
    messages.forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message");

        if (msg.sender_id === currentUserId) {
            div.classList.add("my-message");
        } else {
            div.classList.add("other-message");
        }

        const time = new Date(msg.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

        div.innerHTML = `
            <div>${msg.content_at}</div>
            <div style="font-size:10px;opacity:0.7;margin-top:4px">${time}</div>
        `;

        box.appendChild(div);

        box.scrollTop = box.scrollHeight;
        const input = document.getElementById("messageInput");

        input.oninput = function() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    type: "typing"
                }));
            }
        };
    });

    loadChats();

    if (socket) {
        socket.close();
    }

    socket = new WebSocket(`ws://127.0.0.1:8000/ws/${conversationId}?token=${token}`);

    socket.onopen = function() {
        console.log("WebSocket connected for conversation", conversationId);
    }
    socket.onclose = function() {
        console.log("WebSocket closed");
    }

    socket.onmessage = function(event) {
        const currentUserId = parseInt(localStorage.getItem("user_id"));
        const msg = JSON.parse(event.data);
        console.log("Socket raw event:", event.data);
        
        const box = document.getElementById("messages");

        if (msg.type === "typing" && msg.sender_id !== currentUserId) {
            console.log("Typing condition passed!!")
            showTypingIndicator();
            return;
        }

        if (msg.type === "message"){
            const div = document.createElement("div");
            div.classList.add("message");

            if (msg.sender_id === currentUserId) {
                div.classList.add("my-message");
            } else {
                div.classList.add("other-message");
            }

            const time = new Date(msg.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
            });

            div.innerHTML = `
                <div>${msg.content}</div>
                <div style="font-size:10px;opacity:0.7;margin-top:4px">${time}</div>
            `;

            box.appendChild(div);

            scrollToBottomIfNear(box);
        }    
    };
}

async function sendMessage() {
    const content = document.getElementById("messageInput").value;

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: "message",
            content: content
        }));
    }

    document.getElementById("messageInput").value = "";
}

if (window.location.pathname.includes("chat.html")) {
    const input = document.getElementById("messageInput");

    input.addEventListener("keydown", function(e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
}

if (window.location.pathname.includes("chat.html")) {
    const input = document.getElementById("messageInput");

    let typingTimeout = null;

    input.addEventListener("input", function() {
        console.log("typing event triggered");
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: "typing"
            }));
        }
    });
}

function showTypingIndicator() {
    const box = document.getElementById("messages");

    let typingDiv = document.getElementById("typingIndicator");

    if (!typingDiv) {
        typingDiv = document.createElement("div");
        typingDiv.id = "typingIndicator";
        typingDiv.classList.add("other-message");
        typingDiv.style.fontSize = "12px";
        typingDiv.style.opacity = "0.7";
        typingDiv.innerText = "Typing...";
        box.appendChild(typingDiv);
    }

    // Always move it to bottom
    box.appendChild(typingDiv);

    // Scroll to bottom to make it visible
    box.scrollTop = box.scrollHeight;

    clearTimeout(typingDiv._timeout);

    typingDiv._timeout = setTimeout(() => {
        typingDiv.remove();
    }, 1500);
}