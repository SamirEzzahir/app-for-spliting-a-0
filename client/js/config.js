const API_URL = "http://127.0.0.1:8000";  // Backend URL
let token = localStorage.getItem("token");
const params = new URLSearchParams(window.location.search);
const groupId = params.get("id"); // or "groupId" depending on your URL
