// client/js/expense.js
async function loadExpenses() {
  const res = await fetch(`${API_URL}/expenses/${groupId}`, {
    method: "GET",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token"),
      "Content-Type": "application/json"
    }
  });

  if (!res.ok) {
    return;
  }

 const currentUserId = parseInt(document.getElementById("currentUser").dataset.userid, 10);

console.log("sasa",currentUserId)
  const expenses = await res.json();
  const table = document.getElementById("expensesTable");
  if (!table) return;
  table.innerHTML = "";

  expenses.forEach((e, idx) => {
    const row = document.createElement("tr");

    // participants: join all user_ids (or you can replace with names if you have them)
    const participants = e.splits.map(s => s.username).join(" , ");
    // distribution: show each user's share
    const distribution = e.splits.map(s => `${s.share_amount} ${e.currency}`).join(", ");

   const disabled = e.payer_username !== document.getElementById("currentUser").textContent ? "disabled" : "";
row.innerHTML = `
  <td>${e.id}</td>
  <td>${e.description}</td>
  <td>${e.amount} ${e.currency}</td>
  <td>${e.payer_username ?? "Unknown"}</td>
  <td>${participants}</td>
  <td>${distribution}</td>
  <td>${e.category ?? "-"}</td>
  <td>${new Date(e.created_at).toLocaleString()}</td>
  <td><input type="checkbox" ${e.settled ? "checked" : ""}></td>
  <td>
    <button class="btn btn-sm btn-primary" onclick='openEditExpense(${JSON.stringify(e)})' ${disabled}>Edit</button>
    <button class="btn btn-sm btn-danger" onclick="deleteExpense(${e.id})" ${disabled}>Delete</button>
  </td>
`;

    table.appendChild(row);
  });
}

//console.log("nody: ",expenses.payer_id)
//window.onload = loadExpenses;


// ✅ Delete handler
async function deleteExpense(expenseId) {
  // if (!confirm("Are you sure you want to delete this expense?")) return;

  const res = await fetch(`${API_URL}/expense/${expenseId}`, {
    method: "DELETE",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token")
    }
  });
  //console.log("dele result : ",res)
  if (res.ok) {
    //  alert("Expense deleted");
    loadExpenses(); // refresh
  } else {
    alert("Failed to delete expense");
  }
}







// //////////////////////////////////////////////////



/*


let currentEditExpenseId = null;

async function loadEditMembersList(membersArray) {
  const container = document.getElementById("editMembersList");
  container.innerHTML = "";
  if (!membersArray || !membersArray.length) return; // exit if undefined or empty

  membersArray.forEach(member => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = member.id;
    checkbox.checked = false; // or pre-check if part of the expense
    container.appendChild(checkbox);
    container.appendChild(document.createTextNode(" " + member.username));
    container.appendChild(document.createElement("br"));
  });
}



// ✅ Open Edit Modal
async function openEditExpense(expense) {

// await loadEditMembersList(members); // works
  document.getElementById("editExpenseDesc").value = expense.description;
  document.getElementById("editExpenseAmount").value = expense.amount;

  // Populate members checkboxes
  

  // Check the right members dynamically
  const memberInputs = document.querySelectorAll("#editMembersList input");
  memberInputs.forEach(input => {
    input.checked = expense.splits.some(s => s.user_id === parseInt(input.value));
  });

  // Save the current expense ID
  window.currentEditingExpenseId = expense.id;

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("editExpenseModal"));
  modal.show();
}

*/



/////////////////////New/////////////////////////

// ✅ Fetch members for current group
async function fetchGroupMembers() {
  const res = await fetch(`${API_URL}/groups/${groupId}/members`, {
    headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
  });
  if (!res.ok) return [];
  return await res.json();
}

async function loadEditMembersList(members, expense) {
  const container = document.getElementById("editMembersList");
  if (!container) return;
  container.innerHTML = "";

  members.forEach(member => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = member.user_id;
    checkbox.id = "editMember_" + member.user_id;

    // ✅ Pre-check if this member is already part of the expense
    checkbox.checked = expense.splits.some(s => s.user_id === member.user_id);

    const label = document.createElement("label");
    label.setAttribute("for", checkbox.id);
    label.classList.add("ms-2");
    label.textContent = member.username || member.user_id;

    const div = document.createElement("div");
    div.classList.add("form-check");
    div.appendChild(checkbox);
    div.appendChild(label);

    container.appendChild(div);
  });
}





// Save button handler
document.addEventListener("DOMContentLoaded", () => {
  const saveBtn = document.getElementById("saveEditExpenseBtn");
  if (!saveBtn) return;

  saveBtn.addEventListener("click", async () => {
    

  const description = document.getElementById("editExpenseDesc").value;
  const amount = document.getElementById("editExpenseAmount").value;
  const checkedBoxes = document.querySelectorAll("#editMembersList input:checked");
  const selectedUserIds = Array.from(checkedBoxes).map(cb => parseInt(cb.value));

  // Calculate each share
  const shareAmount = amount / selectedUserIds.length;
  // Generate splits array dynamically
  const splits = selectedUserIds.map(userId => ({
    user_id: userId,
    share_amount: shareAmount
  }));


   


  body = JSON.stringify({ description: description, amount: amount, splits: splits });



  const res = await fetch(`${API_URL}/expense/${window.currentEditingExpenseId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token"),
    },
    body: body
  });

  if (res.ok) {
    alert("Expense updated successfully!");
    loadExpenses();
    bootstrap.Modal.getInstance(document.getElementById("editExpenseModal")).hide();
  } else {
    const error = await res.json();
    alert("Failed to update expense: " + JSON.stringify(error));
  }




});

  });



// ✅ Open Edit Modal
async function openEditExpense(expense) {
  document.getElementById("editExpenseDesc").value = expense.description;
  document.getElementById("editExpenseAmount").value = expense.amount;

  const members = await fetchGroupMembers();   // get all members of group
  await loadEditMembersList(members, expense); // render checkboxes with pre-checks

  window.currentEditingExpenseId = expense.id;

  const modal = new bootstrap.Modal(document.getElementById("editExpenseModal"));
  modal.show();
}






//////////////////////////////////////////////////////



//window.onload = loadExpenses;




document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("balanceId");
  if (btn) { // ✅ check exists
    btn.addEventListener("click", () => {
      window.location.href = `balances.html?id=${groupId}`;
      // your code here
    });
  }
});




async function addExpense() {
  const description = document.getElementById("expenseDesc").value;
  const amount = document.getElementById("expenseAmount").value;
  const currency = "MAD";

  // Example: get groupId from URL (?id=...)
  //const params = new URLSearchParams(window.location.search);
  //const groupId = params.get("id"); // or "groupId" depending on your URL
  // Load members


  // Example: splits must be an array of { user_id, share_amount }
  const checkedBoxes = document.querySelectorAll("#membersList input:checked");
  const selectedUserIds = Array.from(checkedBoxes).map(cb => parseInt(cb.value));
  if (selectedUserIds.length === 0) {
    alert("Please select at least one member!");
    return;
  }
  // Calculate each share
  const shareAmount = amount / selectedUserIds.length;
  // Generate splits array dynamically
  const splits = selectedUserIds.map(userId => ({
    user_id: userId,
    share_amount: shareAmount
  }));


  const res = await fetch(`${API_URL}/expenses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token"),
    },
    body: JSON.stringify({
      group_id: groupId,
      description: description,
      currency: currency,
      amount: amount,
      splits: splits
    }),
  });
  // console.log("check body:", res);
  if (res.ok) {
    const exp = await res.json();
    alert(`Expense created: ${exp.description} (${exp.amount} ${exp.currency})`);
    loadExpenses();
  } else {
    const error = await res.json();
    alert("Failed to create expense: " + JSON.stringify(error));
  }
}



//const params = new URLSearchParams(window.location.search);
//const groupId = params.get("id"); // or "groupId" depending on your URL
// Load members

async function loadMembers(mode = "table") {

  // Load members
  const res = await fetch(`${API_URL}/groups/${groupId}/members`, {
    headers: { "Authorization": "Bearer " + token }
  });
  if (!res.ok) {
    console.error("Failed to fetch members:", res.status);
    return;
  }
  const members = await res.json();


  if (mode === "table") {
    const tbody = document.querySelector("#membersTable");
    if (!tbody) return;
    tbody.innerHTML = "";
    members.forEach(m => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${m.user_id}</td>
        <td>${m.username || m.user_id}</td>
        <td>${m.is_admin ? "Yes" : "No"}</td>
        <td>
          <button class="btn btn-sm btn-warning" onclick="toggleAdmin(${m.user_id}, ${!m.is_admin})">Toggle Admin</button>
          <button class="btn btn-sm btn-danger" onclick="deleteMember(${m.user_id})">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }


  if (mode === "checkbox") {
    const container = document.getElementById("membersList");
    if (!container) return;
    container.innerHTML = "";
    members.forEach(m => {
      const div = document.createElement("div");
      div.className = "form-check";
      div.innerHTML = `
        <input class="form-check-input" type="checkbox" value="${m.user_id}" id="member_${m.user_id}">
        <label class="form-check-label" for="member_${m.user_id}">${m.username || m.user_id}</label>
      `;
      container.appendChild(div);
    });
  }
  return

}






async function addMember() {
  const userId = document.querySelector("#newMemberId").value;
  var isAdmin = document.querySelector("#is_admin").checked;
  if (checkUserExist(userId)) {

    if (!userId) {
      alert("Please provide a valid user ID");
      return;
    }

    const payload = { user_id: Number(userId), is_admin: Boolean(isAdmin) };
    console.log(payload)
    const res = await fetch(`${API_URL}/groups/${groupId}/add_member`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      loadMembers();
    } else {
      const err = await res.json();
      console.error("Error adding member:", err);
      alert("Failed to add member: " + JSON.stringify(err));
    }
  } else {

    console.log(checkUserExist(userId))

  }


}






// Delete member
async function deleteMember(userId) {
  const res = await fetch(`${API_URL}/groups/${groupId}/members/${userId}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + token }
  });
  if (res.ok) loadMembers();
  else alert("Failed to delete member");
}

// Toggle admin status
async function toggleAdmin(userId, newStatus) {
  const res = await fetch(`${API_URL}/groups/${groupId}/members/${userId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ is_admin: newStatus })
  });
  if (res.ok) loadMembers();
  else alert("Failed to update admin status");
}



// Add Member
async function addMember() {
  const userId = document.querySelector("#newMemberId").value;
  var isAdmin = document.querySelector("#is_admin").checked;
  if (checkUserExist(userId)) {

    if (!userId) {
      alert("Please provide a valid user ID");
      return;
    }
    const payload = { user_id: Number(userId), is_admin: Boolean(isAdmin) };
    console.log(payload)
    const res = await fetch(`${API_URL}/groups/${groupId}/add_member`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      loadMembers();
    } else {
      const err = await res.json();
      console.error("Error adding member:", err);
      alert("Failed to add member: " + JSON.stringify(err));
    }
  } else {
    console.log(checkUserExist(userId))
  }
}




// Add member dynamically (without a form)
async function checkUserExist(userId) {
  const res = await fetch(`${API_URL}/users/${userId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });

  if (res.ok) {
    return true; // user exists
  } else {
    const err = await res.json();
    console.error("Error checking member:", err);
    alert("❌ Failed to check member: " + JSON.stringify(err));
    return false;
  }
}


// Download Template
document.getElementById("downloadTemplateBtn").addEventListener("click", async () => {

  if (!groupId) return alert("Enter Group ID");

  const res = await fetch(`${API_URL}/groups/${groupId}/expenses/download-template`, {
    method: "GET"
  });
  if (!res.ok) return alert("Failed to download template");

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `group_${groupId}_template.xlsx`;
  a.click();
  window.URL.revokeObjectURL(url);
});

// Upload Expenses
document.getElementById("uploadExpensesBtn").addEventListener("click", async () => {

  const fileInput = document.getElementById("uploadFile");
  if (!groupId || !fileInput.files.length) return alert("Enter Group ID and select a file");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_URL}/groups/${groupId}/expenses/upload`, {
    method: "POST",
    body: formData
  });

  if (res.ok) {
    document.getElementById("message").innerHTML = `<div class="alert alert-success">Expenses uploaded successfully!</div>`;
  } else {
    document.getElementById("message").innerHTML = `<div class="alert alert-danger">Failed to upload expenses</div>`;
  }
});

// Download Current Expenses
document.getElementById("downloadExpensesBtn").addEventListener("click", async () => {

  if (!groupId) return alert("Enter Group ID");

  const res = await fetch(`${API_URL}/groups/${groupId}/expenses/download`, {
    method: "GET"
  });
  if (!res.ok) return alert("Failed to download expenses");

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `group_${groupId}_expenses.xlsx`;
  a.click();
  window.URL.revokeObjectURL(url);
});


loadExpenses();


// Show members in table
loadMembers("table");

// Show members as checkbox list
loadMembers("checkbox");



