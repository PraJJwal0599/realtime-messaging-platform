let socket = null
let currentConversationId = null;
let oldestMessageId = null;
let isLoadingOlder = false;
let lastRenderedDate = null;

const API_URL = "https://realtime-messaging-backend.onrender.com";
//const API_URL = "http://127.0.0.1:8000";

function scrollToBottomIfNear(box) {
    const threshold = 80; 

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
        li.innerHTML = `
            <div style="font-weight: bold;">${chat.other_user.display_name}</div>
            <div style="font-size: 12px; opacity: 0.7;">@${chat.other_user.username}</div>
            <div style="font-size: 12px; color: green;">Unread: ${chat.unread_count}</div>
        `;
        li.onclick = () => openChat(chat.conversation_id, chat.other_user);
        list.appendChild(li);
    });
}

if (window.location.pathname.includes("chat.html")) {
    showEmptyState();
    loadChats();
}


async function openChat(conversationId, otherUser) {

    const chatArea = document.querySelector(".chat-area");

    if (window.innerWidth <= 768) {
        document.querySelector(".chat-area").classList.add("active");
    }

    const header = document.getElementById("chatHeader");

    if (header && otherUser) {
        header.innerHTML = `
        <span id="backButton" style="cursor:pointer; margin-right:10px;"><-</span>
        ${otherUser.display_name}
        `;

        const backButton = document.getElementById("backButton");

        if (backButton) {
            backButton.onclick = function(event) {
                event.stopPropagation();
                goBack();
            }
        }

        header.onclick = function() {
            openModal("User Info", `Username: @${otherUser.username}`);
        };
    }
    
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

    console.log(messages.map(m => m.created_at));

    oldestMessageId = null;

    const currentUserId = parseInt(localStorage.getItem("user_id"));
    lastRenderedDate = null;

    messages.forEach(msg => {

        if (!oldestMessageId || msg.message_id < oldestMessageId) {
                oldestMessageId = msg.message_id;
            }

        const messageDate = new Date(msg.created_at);
        const formattedDate = messageDate.toDateString();

        if (formattedDate !== lastRenderedDate) {
            const dateDivider = document.createElement("div");
            dateDivider.classList.add("date-divider");
            dateDivider.innerText = messageDate.toLocaleDateString(undefined, {
                year: "numeric",
                month: "long",
                day: "numeric"
            });

            box.appendChild(dateDivider);
            lastRenderedDate = formattedDate;
        }

        const div = document.createElement("div");
        div.classList.add("message");

        if (msg.sender_id === currentUserId) {
            div.classList.add("my-message");
        } else {
            div.classList.add("other-message");
        }

        const time = new Date(msg.created_at);
        const formattedTime = time.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

        div.innerHTML = `
            <div>${msg.content_at || msg.content}</div>
            <div class="timestamp">${formattedTime}</div>
        `;

        box.appendChild(div);
    });

    box.scrollTop = box.scrollHeight;

    box.addEventListener("scroll", () => {

        if (
            box.scrollTop <= 80 &&
            oldestMessageId &&
            !isLoadingOlder
        ) {
            loadOlderMessages(oldestMessageId);
        }
    });

    box.scrollTop = box.scrollHeight;
    const input = document.getElementById("messageInput");

    input.oninput = function() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: "typing"
            }));
        }
    };

    loadChats();

    if (socket) {
        socket.close();
    }

    socket = new WebSocket(`wss://realtime-messaging-backend.onrender.com/ws/${conversationId}?token=${token}`);

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

            const time = new Date(msg.created_at);
            const formattedTime = time.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
            });

            div.innerHTML = `
                <div>${msg.content_at || msg.content}</div>
                <div class = "timestamp">${formattedTime}</div>
            `;

            box.appendChild(div);

            scrollToBottomIfNear(box);
        }    
    };
}

async function loadOlderMessages(beforeId) {

    if (isLoadingOlder) return;
    isLoadingOlder = true;

    const token = localStorage.getItem("token");
    const box = document.getElementById("messages");

    const previousHeight = box.scrollHeight;

    const res = await fetch(
        `${API_URL}/messages/${currentConversationId}?before=${beforeId}&limit=20`,
        {
            headers: { "Authorization": `Bearer ${token}` }
        }
    );

    const olderMessages = await res.json();

    if (!olderMessages.length) {
        isLoadingOlder = false;
        return;
    }

    const fragment = document.createDocumentFragment();

    
    const firstElement = box.firstElementChild;
    let topDate = null;

    if (firstElement) {
        if (firstElement.classList.contains("date-divider")) {
            topDate = firstElement.innerText;
        } else if (firstElement.classList.contains("message")) {
            topDate = firstElement.dataset.readableDate;
        }
    }

    olderMessages.forEach(msg => {

        const messageDate = new Date(msg.created_at);

        const readableDate = messageDate.toLocaleDateString(undefined, {
            year: "numeric",
            month: "long",
            day: "numeric"
        });

        
        if (readableDate !== topDate) {
            const dateDivider = document.createElement("div");
            dateDivider.classList.add("date-divider");
            dateDivider.innerText = readableDate;

            fragment.appendChild(dateDivider);
            topDate = readableDate;
        }

        const div = document.createElement("div");
        div.classList.add("message");

        
        div.dataset.readableDate = readableDate;

        const currentUserId = parseInt(localStorage.getItem("user_id"));

        if (msg.sender_id === currentUserId) {
            div.classList.add("my-message");
        } else {
            div.classList.add("other-message");
        }

        const formattedTime = messageDate.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

        div.innerHTML = `
            <div>${msg.content_at || msg.content}</div>
            <div class="timestamp">${formattedTime}</div>
        `;

        fragment.appendChild(div);
    });

    box.prepend(fragment);

    oldestMessageId = olderMessages[0].message_id;

    const newHeight = box.scrollHeight;
    box.scrollTop = box.scrollTop + (newHeight - previousHeight);

    isLoadingOlder = false;
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

    box.onscroll = async function() {
        if (box.scrollTop === 0 && oldestMessageId) {
            await loadOlderMessages(oldestMessageId);
        }
    }

    clearTimeout(typingDiv._timeout);

    typingDiv._timeout = setTimeout(() => {
        typingDiv.remove();
    }, 1500);
}

async function signup() {
    const email = document.getElementById("signupEmail").value;
    const username = document.getElementById("signupUsername").value;
    const displayName = document.getElementById("signupDisplayName").value;
    const password = document.getElementById("signupPassword").value;

    const res = await fetch(`${API_URL}/auth/signup`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            username: username,
            display_name: displayName,
            password: password
        })
    });

    if (!res.ok) {
        document.getElementById("signupError").innerText =
            "Signup failed. Email may already exist.";
        return;
    }

    // Auto-login after successful signup
    const loginRes = await fetch(
        `${API_URL}/auth/login?email=${email}&password=${password}`,
        { method: "POST" }
    );

    if (!loginRes.ok) {
        window.location.href = "index.html";
        return;
    }

    const loginData = await loginRes.json();
    localStorage.setItem("token", loginData.access_token);

    const meRes = await fetch(`${API_URL}/auth/me`, {
        headers: {
            "Authorization": `Bearer ${loginData.access_token}`
        }
    });

    if (meRes.ok) {
        const meData = await meRes.json();
        localStorage.setItem("user_id", meData.id);
    }

    window.location.href = "index.html";
}

async function startNewChat() {
    const token = localStorage.getItem("token");
    const username = document.getElementById("newChatUsername").value;

    if (!username) {
        alert("Enter a username");
        return;
    }

    const confirmStart = confirm(`Start conversation with ${username}?`);
    if (!confirmStart) return;

    const res = await fetch(
        `${API_URL}/conversations/direct/${username}`,
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    if (!res.ok) {
        alert("User not found or cannot start chat.");
        return;
    }

    const data = await res.json();

    loadChats();
    openChat(data.conversation_id);

    document.getElementById("newChatUsername").value = "";
}

function showEmptyState() {
    if (socket) {
        socket.close();
        socket = null;
    }

    currentConversationId = null;

    const header = document.getElementById("chatHeader");
    const box = document.getElementById("messages");

    if (header) header.innerHTML = "";
    if (box) {
        box.innerHTML = `
            <div style="
                margin: auto;
                text-align: center;
                opacity: 0.6;
                font-size: 18px;
            ">
                Select a conversation to start chatting
            </div>
        `;
    }
}

function goBack() {
    if (socket) {
        socket.close();
        socket = null;
    }

    currentConversationId = null;
    showEmptyState();

    if (window.innerWidth <= 768) {
        document.querySelector(".chat-area").classList.remove("active");
    }
}

function toggleStartChat() {
    const box = document.getElementById("startChatBox");

    if (box.classList.contains("hidden")) {
        box.classList.remove("hidden");
    } else {
        box.classList.add("hidden");
    }
}

function openModal(title, content) {
    document.getElementById("modalTitle").innerText = title;
    document.getElementById("modalContent").innerText = content;
    document.getElementById("modalOverlay").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modalOverlay").classList.add("hidden");
}