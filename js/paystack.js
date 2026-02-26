function payWithPaystack(email, plan) {
  let amount = plan === 'weekly' ? 745000 : 2755000; // weekly/monthly in kobo
  let handler = PaystackPop.setup({
    key: 'pk_test_8f53865d8bded27a891f25b99bcdc15ccd9c6d6e', // replace with your Paystack public key
    email: email,
    amount: amount,
    currency: "NGN",
    callback: function(response) {
      // Payment successful → save VIP info
      let days = plan === 'weekly' ? 7 : 30;
      let expiry = new Date();
      expiry.setDate(expiry.getDate() + days);

      localStorage.setItem("vip_active", "true");
      localStorage.setItem("vip_expiry", expiry);

      // Redirect to VIP page
      window.location.href = "vip.html";
    },
    onClose: function() {
      alert("Payment cancelled");
    }
  });
  handler.openIframe();
}
