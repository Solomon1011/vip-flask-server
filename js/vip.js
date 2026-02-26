// VIP Expiry Check
const vipActive = localStorage.getItem("vip_active");
const vipExpiry = localStorage.getItem("vip_expiry");
const now = new Date();

if (vipActive === "true" && vipExpiry && now < new Date(vipExpiry)) {
  // VIP still valid → unlock tips
  document.querySelectorAll(".blur").forEach(el => el.classList.remove("blur"));
  document.querySelectorAll(".lock").forEach(el => el.style.display = "none");
} else {
  // VIP expired or not active
  localStorage.removeItem("vip_active");
  localStorage.removeItem("vip_expiry");

  alert("Your VIP subscription has expired. Please renew.");
  window.location.href = "index.html"; // redirect to subscription page
}
