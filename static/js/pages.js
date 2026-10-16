document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-register-role]");
  if (!button) return;
  window.GreenCertApp.notice("Role registration becomes available after the RoleRegistry deployment is configured.");
});
