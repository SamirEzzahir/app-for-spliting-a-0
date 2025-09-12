const API_URL = "http://127.0.0.1:8000";  // Backend URL
let token = localStorage.getItem("token");

// ---------------------- AUTH ----------------------

async function registerUser() {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.getElementById("name").value,
      username: document.getElementById("username").value,
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

  const res = await fetch(`${API_URL}/login`, { method: "POST", body: data });

  if (res.ok) {
    const json = await res.json();
    token = json.access_token;
    localStorage.setItem("token", token);
    alert("Login successful!");
    window.location.href = "items.html"; // Redirect after login
  } else {
    alert("Login failed!");
  }
}

function logoutUser() {
  localStorage.removeItem("token");
  token = null;
  window.location.href = "login.html";
}

// ---------------------- ITEMS CRUD ----------------------



async function loadItems() {

/*const res = await fetch(`${API_URL}/items`, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }},*/

const res = await fetch(`${API_URL}/items`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const items = await res.json();
  
  const tbody = document.querySelector('#itemsTable tbody');
  tbody.innerHTML = ''; // clear previous rows

  items.forEach(item => {
    const tr = document.createElement('tr');
    const createdAt = new Date(item.created_at);

    tr.innerHTML = `
      <td>${item.id}</td>
      <td>${item.name}</td>
      <td>${item.price} Dhs</td>
      <td>${createdAt.toLocaleString()}</td>
      <td>${item.owner_name}</td>
      <td>
        <button class="btn btn-sm btn-warning me-2" onclick="editItem(${item.id}, '${item.name}', ${item.price}, '${item.created_at}')">Edit</button>
        <button class="btn btn-sm btn-danger" onclick="deleteItem(${item.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}


async function addItem() {
  if (!token) return alert("Login first!");

  const res = await fetch(`${API_URL}/items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({
      name: document.getElementById("itemName").value,
      price: parseFloat(document.getElementById("itemPrice").value)
    })
  });

  if (res.ok) {
   loadItems();
    document.getElementById("itemName").value = "";
    document.getElementById("itemPrice").value = "";
  } else {
    alert("Error adding item!");
  }
}

async function editItem(id, name, price) {
  const newName = prompt("Edit name:", name);
  const newPrice = prompt("Edit price:", price);
  if (!newName || !newPrice) return;

  const res = await fetch(`${API_URL}/items/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ name: newName, price: parseFloat(newPrice) })
  });

  if (res.ok) {
    loadItems();
  } else {
    alert("Error updating item!");
  }
}

async function deleteItem(id) {
  const res = await fetch(`${API_URL}/items/${id}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + token }
  });

  if (res.ok) {
    loadItems();
  } else {
    alert("Error deleting item!");
  }
}
