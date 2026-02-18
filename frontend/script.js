const API = "http://127.0.0.1:8000";

function saveToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })
    });

    if (res.ok) {
        document.getElementById("message").innerText = "Registered! Now login.";
    }
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API}/login`, {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    // script.js update
if (res.ok) {
    saveToken(data.access_token);
    window.location.href = "dashboard.html";
} else {
    document.getElementById("message").innerText = data.detail || "Login Failed";
}
}

async function loadMeetings() {
    const res = await fetch(`${API}/meetings/`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });

    const meetings = await res.json();

    const container = document.getElementById("meetings");
    container.innerHTML = "";

    meetings.forEach(m => {
        container.innerHTML += `
            <div>
                <h4>${m.title}</h4>
                <button onclick="viewMeeting(${m.id})">View</button>
            </div>
        `;
    });
}

function viewMeeting(id) {
    localStorage.setItem("meetingId", id);
    window.location.href = "meeting.html";
}

async function createMeeting() {
    const title = document.getElementById("title").value;
    const date = document.getElementById("date").value;
    const description = document.getElementById("description").value;

    await fetch(`${API}/meetings/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify({ title, date, description })
    });

    loadMeetings();
}

async function loadMeetingDetails() {
    const id = localStorage.getItem("meetingId");

    const res = await fetch(`${API}/meetings/${id}`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });

    const meeting = await res.json();

    document.getElementById("meetingTitle").innerText = meeting.title;
    document.getElementById("meetingDesc").innerText = meeting.description;
}

async function analyzeMeeting() {
    const id = localStorage.getItem("meetingId");

    const res = await fetch(`${API}/meetings/${id}/health`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });

    const data = await res.json();

    document.getElementById("analysis").innerText =
        `Sentiment: ${data.sentiment}\nRisk: ${data.risk_level}\nSummary: ${data.summary}`;
}

function exportMeeting() {
    const id = localStorage.getItem("meetingId");
    window.open(`${API}/meetings/${id}/export`, "_blank");
}
