async function loadNavbar() {
  const res = await fetch("partials/navbar.html");
  document.getElementById("navbar").innerHTML = await res.text();

  // Attach logout logic
  document.getElementById("logoutBtn")?.addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "login.html";
  });
}

// Call on page load
loadNavbar();
