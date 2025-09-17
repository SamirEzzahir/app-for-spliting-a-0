let groups = [];

document.getElementById("createGroupForm").addEventListener("submit", function(e){
  e.preventDefault();
  const name = document.getElementById("groupName").value;
  const type = document.getElementById("groupType").value;
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
