async function loginUser() {
const data = new URLSearchParams();
  data.append("username", document.getElementById("loginUsername").value);
  data.append("password", document.getElementById("loginPassword").value);

  const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: data });

  if (res.ok) {
    const json = await res.json();
   // console.log("username : ",res.username)
    token = json.access_token;
    localStorage.setItem("token", token);
   // alert("Login successful!");
    window.location.href = "index.html"; // Redirect after login
  } else {
    alert("Login failed!");
  }
}

   // Example logout logic
    document.getElementById("logoutBtn").addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = "login.html";
    });






// client/js/login.js
// Register
async function registerUser(event) {
  event.preventDefault(); // prevent page refresh

  try {
    await apiRequest("/auth/register", "POST", {
      username: document.getElementById("username").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value
    });

    window.location.href = "login.html"; // go to login after success
  } catch (err) {
    alert("Registration failed: " + err.message);
  }
}
