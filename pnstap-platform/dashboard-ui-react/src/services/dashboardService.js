const API_URL = "http://127.0.0.1:8000";

export async function getDashboardData() {
    const response = await fetch(`${API_URL}/api/dashboard/`);

    if (!response.ok) {
        throw new Error("Failed to fetch dashboard data.");
    }

    return await response.json();
}
export async function chatWithLyromi(message) {

    const response = await fetch(
        `${API_URL}/api/lyromi/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message
            })
        }
    );

    if (!response.ok) {

        throw new Error("Lyromi request failed.");

    }

    return await response.json();

}