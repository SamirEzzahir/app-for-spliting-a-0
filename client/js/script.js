const API_URL = "http://127.0.0.1:8011";  // Backend URL
let token = localStorage.getItem("token");

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
  if (res.ok) {
    alert("Login successful!");
  } else {
    alert("Login failed!");
  }
}

async function loginUser() {
const data = new URLSearchParams();
  data.append("username", document.getElementById("loginUsername").value);
  data.append("password", document.getElementById("loginPassword").value);

  const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: data });

  if (res.ok) {
    const json = await res.json();
    token = json.access_token;
    localStorage.setItem("token", token);
    alert("Login successful!");
    window.location.href = "index.html"; // Redirect after login
  } else {
    alert("Login failed!");
  }
}

function logoutUser() {
  localStorage.removeItem("token");
  token = null;
  window.location.href = "login.html";
}

/**/
// Fetch and render users
async function loadUsers() {
  const res = await fetch(`${API_URL}/users`, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
        });


  if (!res.ok) return console.error("Failed to load users");


  const users = await res.json();
  const tbody = document.querySelector("#usersTable tbody");
  tbody.innerHTML = "";
  users.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${u.id}</td><td>${u.username}</td><td>${u.email}</td>`;
    tbody.appendChild(tr);
  });
}

/*
async function loadUsers() {
     
    try {
        const response = await fetch(`${API_URL}/users`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const users = await response.json();
        console.log("Users:", users);
        // populate your HTML table here
    } catch (err) {
        console.error("Failed to load users:", err);
    }
}
*/

// Fetch and render groups
async function loadGroups() {
  const res = await fetch(`${API_URL}/groups`, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
        });
  if (!res.ok) return console.error("Failed to load groups");
  const groups = await res.json();
  const tbody = document.querySelector("#groupsTable tbody");
  tbody.innerHTML = "";
  groups.forEach(g => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${g.id}</td><td>${g.name}</td><td>${g.currency}</td><td>${g.owner_id}</td>`;
    tbody.appendChild(tr);
  });
}

// Fetch and render expenses
async function loadExpenses() {
  const res = await fetch(`${API_URL}/expenses`, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
        });
  if (!res.ok) return console.error("Failed to load expenses");
  const expenses = await res.json();
  const tbody = document.querySelector("#expensesTable tbody");
  tbody.innerHTML = "";
  expenses.forEach(e => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${e.id}</td><td>${e.group_id}</td><td>${e.payer_id}</td><td>${e.description}</td><td>${e.amount}</td><td>${e.currency}</td>`;
    tbody.appendChild(tr);
  });
}


// Create group
document.getElementById("groupForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("groupName").value.trim();
    const currency = document.getElementById("currency").value.trim();
    const membersStr = document.getElementById("members").value.trim();
    const member_ids = membersStr ? membersStr.split(",").map(id => parseInt(id.trim())) : [];

    try {
        const response = await fetch(`${API_URL}/groups`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ name, currency, member_ids })
        });

        if (!response.ok) {
            const err = await response.json();
            return showMessage("danger", "Failed to create group: " + err.detail);
        }

        const group = await response.json();
        showMessage("success", `Group "${group.name}" created successfully!`);
        loadGroups(); // Refresh table
        document.getElementById("groupForm").reset();
    } catch (err) {
        showMessage("danger", "Error: " + err.message);
    }
});

// Show Bootstrap alert messages
function showMessage(type, text) {
    const msgDiv = document.getElementById("message");
    msgDiv.innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`;
}

// Fetch and render groups
async function loadGroups() {
    try {
        const response = await fetch(`${API_URL}/groups`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        if (!response.ok) throw new Error("Failed to load groups");
        const groups = await response.json();

        const tbody = document.querySelector("#groupsTable tbody");
        tbody.innerHTML = "";
        groups.forEach(g => {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${g.id}</td><td>${g.name}</td><td>${g.currency}</td><td>${g.owner_id}</td>`;
            tbody.appendChild(tr);
        });
    } catch (err) {
        showMessage("danger", err.message);
    }
}

// Load groups on page load
window.addEventListener("DOMContentLoaded", loadGroups);

// Load all tables on page load
window.addEventListener("DOMContentLoaded", () => {
  loadUsers();
  loadGroups();
  loadExpenses();
});


/*const API_URL = "http://127.0.0.1:8010";  // Backend URL
let token = localStorage.getItem("token");

// ---------------------- AUTH ----------------------

async function registerUser() {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value
    })
  });
  alert(await res.text());
}

async function loginUser() {
const data = new URLSearchParams();
  data.append("username", document.getElementById("loginUsername").value);
  data.append("password", document.getElementById("loginPassword").value);

  const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: data });

  if (res.ok) {
    const json = await res.json();
    token = json.access_token;
    localStorage.setItem("token", token);
    alert("Login successful!");
    window.location.href = "index.html"; // Redirect after login
  } else {
    alert("Login failed!");
  }
}

function logoutUser() {
  localStorage.removeItem("token");
  token = null;
  window.location.href = "login.html";
}

/*
// Load all groups
async function loadGroups() {
  const res = await fetch(`${API_URL}/groups`);
  const data = await res.json();
  const ul = document.getElementById("groups");
  ul.innerHTML = "";
  data.forEach(group => {
    const li = document.createElement("li");
    li.textContent = `${group.id} - ${group.name}`;
    ul.appendChild(li);
  });
}
loadGroups();




// Submit expense form

document.getElementById("expenseForm").onsubmit = async (e) => {
  e.preventDefault();
  const expense = {
    group_id: parseInt(document.getElementById("group_id").value),
    payer_id: parseInt(document.getElementById("payer_id").value),
    description: document.getElementById("description").value,
    amount: parseFloat(document.getElementById("amount").value)
  };
  const res = await fetch(`${API_URL}/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(expense)
  });
  const data = await res.json();
  console.log("Added expense:", data);
};

*/


let groups = [];

document.getElementById("createGroupForm").addEventListener("submit", function(e){
  e.preventDefault();
  const name = document.getElementById("groupName").value;
  const type = document.getElementById("groupType").value;
  const ss = document.getElementById("ll").value;
  const group = { id: Date.now(), name, type, members: [], expenses: [] };
  groups.push(group);
  renderGroups();
  bootstrap.Modal.getInstance(document.getElementById('createGroupModal')).hide();
});

function renderGroups() {
  const list = document.getElementById("groupsList");
  list.innerHTML = "";
  groups.forEach(g => {
    const item = document.createElement("div");
    item.className = "list-group-item d-flex justify-content-between align-items-center";
    item.innerHTML = `
      <span>${g.name} (${g.type})</span>
      <button class="btn btn-sm btn-primary" onclick="openGroup(${g.id})">Open</button>
    `;
    list.appendChild(item);
  });
}

function openGroup(id) {
  const group = groups.find(g => g.id === id);
  localStorage.setItem("currentGroup", JSON.stringify(group));
  window.location.href = "group.html";
}