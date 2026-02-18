const API = "http://localhost:8000";

function saveToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

function clearToken() {
    localStorage.removeItem("token");
    localStorage.removeItem("meetingId");
}

function logout() {
    clearToken();
    window.location.href = "/";
}

function backToDashboard() {
    window.location.href = "/dashboard.html";
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        showMessage("Please enter email and password", "error");
        return;
    }

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })
    });

    if (res.ok) {
        showMessage("✅ Registered successfully! Now login.", "success");
        document.getElementById("email").value = "";
        document.getElementById("password").value = "";
    } else {
        const data = await res.json();
        showMessage("❌ " + (data.detail || "Registration failed"), "error");
    }
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        showMessage("Please enter email and password", "error");
        return;
    }

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const res = await fetch(`${API}/login`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            saveToken(data.access_token);
            window.location.href = "/dashboard.html";
        } else {
            showMessage("❌ " + (data.detail || "Login failed"), "error");
        }
    } catch (error) {
        showMessage("❌ Connection error. Make sure the server is running.", "error");
    }
}

function showMessage(message, type) {
    let msgEl = document.getElementById("message");
    if (!msgEl) {
        msgEl = document.createElement("p");
        msgEl.id = "message";
        document.body.appendChild(msgEl);
    }
    msgEl.innerText = message;
    msgEl.className = type === "error" ? "message-box error" : "message-box success";
}

async function loadMeetings() {
    try {
        const res = await fetch(`${API}/meetings/`, {
            headers: { "Authorization": `Bearer ${getToken()}` }
        });

        if (res.status === 401) {
            logout();
            return;
        }

        const meetings = await res.json();

        const container = document.getElementById("meetings");
        if (meetings.length === 0) {
            container.innerHTML = "<p style='text-align: center; color: #999;'>No meetings yet. Create one!</p>";
        } else {
            container.innerHTML = "";
            meetings.forEach(m => {
                container.innerHTML += `
                    <div>
                        <h4>${m.title}</h4>
                        <p style="color: #666; font-size: 0.9rem;">📅 ${m.date}</p>
                        <p style="color: #666; font-size: 0.85rem; margin: 0.5rem 0;">${m.description.substring(0, 100)}...</p>
                        <button onclick="viewMeeting(${m.id})" style="width: 100%; margin-top: 0.8rem;">View Details</button>
                    </div>
                `;
            });
        }
    } catch (error) {
        console.error("Error loading meetings:", error);
    }
}

function viewMeeting(id) {
    localStorage.setItem("meetingId", id);
    window.location.href = "/meeting.html";
}

async function createMeeting() {
    const title = document.getElementById("title").value;
    const date = document.getElementById("date").value;
    const description = document.getElementById("description").value;

    if (!title || !date || !description) {
        alert("Please fill in all fields");
        return;
    }

    try {
        const res = await fetch(`${API}/meetings/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${getToken()}`
            },
            body: JSON.stringify({ title, date, description })
        });

        if (res.ok) {
            document.getElementById("title").value = "";
            document.getElementById("date").value = "";
            document.getElementById("description").value = "";
            alert("✅ Meeting created successfully!");
            loadMeetings();
        } else {
            alert("❌ Failed to create meeting");
        }
    } catch (error) {
        console.error("Error creating meeting:", error);
    }
}

async function loadMeetingDetails() {
    const id = localStorage.getItem("meetingId");

    try {
        const res = await fetch(`${API}/meetings/${id}`, {
            headers: { "Authorization": `Bearer ${getToken()}` }
        });

        if (!res.ok) {
            alert("Meeting not found or access denied");
            window.location.href = "/dashboard.html";
            return;
        }

        const meeting = await res.json();

        document.getElementById("meetingTitle").innerText = `📅 ${meeting.title} (${meeting.date})`;
        document.getElementById("meetingDesc").innerText = meeting.description;
    } catch (error) {
        console.error("Error loading meeting:", error);
    }
}

async function analyzeMeeting() {
    const id = localStorage.getItem("meetingId");

    try {
        const res = await fetch(`${API}/meetings/${id}/health`, {
            headers: { "Authorization": `Bearer ${getToken()}` }
        });

        if (res.ok) {
            const data = await res.json();

            const analysis = document.getElementById("analysis");
            analysis.innerHTML = `
                <strong>🤖 AI Analysis Results:</strong><br><br>
                <strong>Sentiment:</strong> ${data.sentiment || "N/A"}<br>
                <strong>Risk Level:</strong> ${data.risk_level || "N/A"}<br>
                <strong>Summary:</strong> ${data.summary || "No summary available"}
            `;
        } else {
            alert("Failed to analyze meeting");
        }
    } catch (error) {
        console.error("Error analyzing meeting:", error);
    }
}

function exportMeeting() {
    const id = localStorage.getItem("meetingId");
    window.open(`${API}/meetings/${id}/export`, "_blank");
}
