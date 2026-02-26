const vipActive = localStorage.getItem("vip_active");
const vipExpiry = localStorage.getItem("vip_expiry");
const now = Date.now();

if (vipActive === "true" && vipExpiry && now < vipExpiry) {
  // VIP still valid → unlock
  document.querySelectorAll(".blur").forEach(el => {
    el.classList.remove("blur");
  });
  document.querySelectorAll(".lock").forEach(el => {
    el.style.display = "none";
  });
} else {
  // VIP expired or not active
  localStorage.removeItem("vip_active");
  localStorage.removeItem("vip_expiry");

  alert("VIP expired. Please renew to see tips.");
}
