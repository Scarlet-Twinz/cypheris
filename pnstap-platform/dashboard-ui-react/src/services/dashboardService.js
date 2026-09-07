const API_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function authHeaders() {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseResponse(response, fallback) {
    if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");
        throw new Error("Your session has expired. Please sign in again.");
    }
    if (!response.ok) {
        let detail = fallback;
        try {
            const data = await response.json();
            detail = data?.detail || detail;
        } catch { /* keep fallback */ }
        throw new Error(detail);
    }
    return response.json();
}

export async function getDashboardData() {
    const response = await fetch(`${API_URL}/api/dashboard/`, { headers: authHeaders() });
    return parseResponse(response, "Failed to fetch dashboard data.");
}

export async function chatWithLyromi(message) {
    const response = await fetch(`${API_URL}/api/lyromi/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ message }),
    });
    return parseResponse(response, "Lyromi request failed.");
}
