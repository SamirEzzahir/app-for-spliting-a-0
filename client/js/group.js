
async function createGroup() {
  const name = document.getElementById("groupName").value;
  const currency = document.getElementById("groupCurrency").value;
  const checkedBoxes = document.querySelectorAll("#usersList input:checked");
  const memberIds = Array.from(checkedBoxes).map(cb => parseInt(cb.value));
  if (memberIds.length === 0) {
    alert("Please select at least one member!");
    return;
  }
  const res = await fetch(`${API_URL}/groups`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token"),
    },
    body: JSON.stringify({
      name: name,
      currency: currency,
      member_ids: memberIds
    })
  });

  if (res.ok) {
    const group = await res.json();
    alert(`Group created: ${group.name}`);
    window.location.href = `expenses.html?id=${group.id}`;
  } else {
    const err = await res.json();
    alert("Failed to create group: " + JSON.stringify(err));
  }
}

async function loadGroups() {
  const res = await fetch(`${API_URL}/groups`, {
    method: "GET",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token"),
      "Content-Type": "application/json"
    }
  });
  if (!res.ok) {
    return;
  }

  const groups = await res.json();
  const table = document.getElementById("groupsTable");
  table.innerHTML = "";

  if (groups.length === 0) {
    table.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No groups found</td></tr>`;
    return;
  }

  groups.forEach(g => {
    const row = document.createElement("tr");
    row.innerHTML = `
          <td>${g.id}</td>
          <td>${g.name}</td>
          <td>${g.currency}</td>
          <td>${g.owner_id}</td>
          <td>${new Date(g.created_at).toLocaleString()}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="openGroup(${g.id})">Open</button>
            <button class="btn btn-sm btn-warning"  onclick="editGroup(
    document.getElementById('editName').value,
    document.getElementById('editCurrency').value)">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteGroup(${g.id})">Delete</button>
          </td>
        `;
    table.appendChild(row);
  });
}



async function deleteGroup(groupId) {
  if (!groupId) return;

  //if (!confirm("Are you sure you want to delete this group?")) return;

  const res = await fetch(`${API_URL}/groups/${groupId}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + token }
  });

  if (res.ok) {
    //alert("Group deleted successfully");
    loadGroups(); // reload table
  } else {
    const err = await res.json();
    alert("Failed to delete group: " + JSON.stringify(err));
  }

}


async function editGroup(newName, newCurrency) {
  if (!newName && !newCurrency) {
    alert("Provide a new name or currency");
    return;
  }

  const payload = {};
  if (newName) payload.name = newName;
  if (newCurrency) payload.currency = newCurrency;

  const res = await fetch(`${API_URL}/groups/${groupId}`, {
    method: "PUT",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    const updatedGroup = await res.json();
    alert(`Group updated: ${updatedGroup.name} (${updatedGroup.currency})`);
    loadGroupDetails(); // optional: reload group info
  } else {
    const err = await res.json();
    console.error("Update failed:", err);
    alert("Failed to update group: " + JSON.stringify(err));
  }
}


function openGroup(groupId) {
  // redirection to group details page
  window.location.href = `expenses.html?id=${groupId}`;
}



 loadGroups();