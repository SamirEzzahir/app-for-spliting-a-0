// client/js/navbar.js
async function loadNavbar() {
  const navbarContainer = document.getElementById("navbar");
  if (!navbarContainer) return;

  const res = await fetch("partials/navbar.html");
  navbarContainer.innerHTML = await res.text();

  // Highlight active link
  const currentPage = window.location.pathname.split("/").pop();
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === currentPage) {
      link.classList.add("active");
    }
  });

  // Add logout logic
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = "login.html";
    });
  }
}

// Call on page load
document.addEventListener("DOMContentLoaded", loadNavbar);
