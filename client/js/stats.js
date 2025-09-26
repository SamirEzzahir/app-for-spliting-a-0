// stats.js
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // Fetch user stats
  fetch(API_URL + "/stats/user", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => renderUserChart(data))
    .catch(err => console.error("User stats error:", err));
 
  // Fetch current user expenses per group
  fetch(API_URL + "/stats/user/groups", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(data =>  renderAllGroupsChart(data))
    .catch(err => console.error("User groups stats error:", err));
});
  // Fetch all groups (global)
  fetch(`${API_URL}/stats/group/${groupId}`, {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => renderGroupChart(data))
    .catch(err => console.error("Group stats error:", err));




function renderUserChart(data) {
  const ctx = document.getElementById("userExpensesChart");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: [data.username],
      datasets: [{
        label: "Your Total Expenses",
        data: [data.total_expenses],
        backgroundColor: ["#0d6efd"]
      }]
    }
  });
}

function renderGroupChart(data) {
  const ctx = document.getElementById("groupExpensesChart");

  const labels = data.map(g => g.group_name);
  const values = data.map(g => g.amount);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Total Expenses per Group (All Users)",
        data: values,
        backgroundColor: ["#0dcaf0","#6610f2","#fd7e14","#198754","#dc3545"]
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } }
    }
  });
}

function renderAllGroupsChart(data) {
  const ctx = document.getElementById("allGroupsChart");

  const labels = data.map(g => g.group_name);
  const values = data.map(g => g.amount);

  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Your Expenses per Group",
        data: values,
        borderColor: "#0d6efd",
        fill: true,
        backgroundColor: "rgba(13,110,253,0.2)"
      }]
    }
  });
}
