

async function apiRequest(endpoint, method = "GET", body = null) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {})
  };

  try {
    const res = await fetch(`${API_URL}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "API request failed");
    }

    return await res.json();
  } catch (err) {
    console.error("API Error:", err.message);
    throw err;
  }
}
