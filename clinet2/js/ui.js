function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-bg-${type} border-0 show`;
  toast.role = "alert";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
