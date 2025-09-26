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
 
  

// client/js/login.js
async function registerUser() {

  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("username").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value
    })
  });
  console.log(res)
 
  if (res.ok) {
  //  alert("Login successful!");
      window.location.href = "login.html";
  } else {
    alert("Login failed!");
  }
}

