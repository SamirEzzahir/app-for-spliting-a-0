let group = JSON.parse(localStorage.getItem("currentGroup"));
document.getElementById("groupTitle").innerText = `${group.name} (${group.type})`;

document.getElementById("addMemberBtn").addEventListener("click", addMember);
document.getElementById("addExpenseForm").addEventListener("submit", addExpenseForm);

function addMember() {
  const name = prompt("Enter member name:");
  if (name) {
    group.members.push({ name: name.trim(), balance: 0 });
    saveGroup();
    alert(name + " added!");
    renderParticipants();
  }
}

// Render checkboxes inside modal
function renderParticipants() {
  const container = document.getElementById("participantsList");
  container.innerHTML = "";
  group.members.forEach((m, idx) => {
    const div = document.createElement("div");
    div.className = "form-check";
    div.innerHTML = `
      <input class="form-check-input" type="checkbox" id="participant-${idx}" value="${m.name}">
      <label class="form-check-label" for="participant-${idx}">${m.name}</label>
    `;
    container.appendChild(div);
  });
}

function addExpenseForm(e) {
  e.preventDefault();

  const description = document.getElementById("expenseDesc").value;
  const amount = parseFloat(document.getElementById("expenseAmount").value);

  // Get selected participants
  const checkboxes = document.querySelectorAll("#participantsList input:checked");
  const participants = Array.from(checkboxes).map(cb => cb.value);

  if (participants.length === 0) {
    alert("Please select at least one participant");
    return;
  }

  // Save expense
  group.expenses.push({ description, amount, participants });

  // Split amount equally
  const perPerson = amount / participants.length;
  participants.forEach(p => {
    const member = group.members.find(m => m.name === p);
    if (member) member.balance += perPerson;
  });

  saveGroup();
  renderExpenses();

  // Close modal
  bootstrap.Modal.getInstance(document.getElementById('addExpenseModal')).hide();
  document.getElementById("addExpenseForm").reset();
}

function renderExpenses() {
  const list = document.getElementById("expenseList");
  list.innerHTML = "";
  group.expenses.forEach(e => {
    const item = document.createElement("li");
    item.className = "list-group-item";
    item.innerHTML = `${e.description}: ${e.amount} - Participants: ${e.participants.join(", ")}`;
    list.appendChild(item);
  });
}

function saveGroup() {
  localStorage.setItem("currentGroup", JSON.stringify(group));
}

renderParticipants();
renderExpenses();
