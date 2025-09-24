

// Load users into checkboxes
async function loadUsers(mode = "checkbox") {
  const res = await fetch(`${API_URL}/users`, {
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    }
  });

  if (!res.ok) {
    console.error("Failed to fetch users:", res.status);
    return;
  }
  const users = await res.json();

  if (mode === "checkbox") {
    const container = document.getElementById("usersList");
    container.innerHTML = "";
    users.forEach(user => {
      const div = document.createElement("div");
      div.className = "form-check";
      div.innerHTML = `
        <input class="form-check-input" type="checkbox" value="${user.id}" id="user_${user.id}">
        <label class="form-check-label" for="user_${user.id}">ID:${user.id} ${user.username}</label>
      `;
      container.appendChild(div);
    });
  }

  if (mode === "table") {
    const tbody = document.querySelector("#usersTable tbody");
    tbody.innerHTML = "";
    users.forEach(u => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.username}</td>
        <td>${u.email}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}
async function getUserById(userId) {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`${API_URL}/users/${userId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
      }
    });

    if (!res.ok) {
      const err = await res.json();
      console.error("Error fetching user:", err);
      return null;
    }

    const user = await res.json();

    return user; // { id, email, username }
  } catch (err) {
    console.error("Network error fetching user:", err);
    return null;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const currentUserSpan = document.getElementById("currentUser");

  async function loadCurrentUser() {
    try {
      const res = await fetch(`${API_URL}/currentUser`, {
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json"
        }
      });
      if (!res.ok) {
        console.error("Failed to fetch current user:", res.status);
        return;
      }
      const user = await res.json();
      
      currentUserSpan.textContent = `👤 ${user.username}`;
    } catch (err) {
      console.error("Error fetching current user:", err);
    }
  }

  // Run on page load
  loadCurrentUser();


});




// Example: Add member dynamically
// addMember(5); // adds user with ID 5

// Load groups on page load


loadUsers("checkbox");

// Show users as a table
loadUsers("table");

