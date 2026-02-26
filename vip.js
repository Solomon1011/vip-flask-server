// check VIP status saved after Paystack payment
const isVIP = localStorage.getItem("vip_active");

if (isVIP === "true") {
  document.querySelectorAll(".blur").forEach(el => {
    el.classList.remove("blur");
  });
  document.querySelectorAll(".lock").forEach(el => {
    el.style.display = "none";
  });
}
