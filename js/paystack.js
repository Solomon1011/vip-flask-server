function payWithPaystack(email) {
  let handler = PaystackPop.setup({
    key: 'pk_test_xxxxxxxxxxxxx', // replace with your Paystack PUBLIC key
    email: email,
    amount: 200000, // 2000 NGN (amount is in kobo)
    currency: "NGN",
    callback: function (response) {
      alert("Payment successful!");

      // Save expiry date (30 days)
      let expiry = new Date();
      expiry.setDate(expiry.getDate() + 30);

      localStorage.setItem("vip_expiry", expiry);
      localStorage.setItem("vip_user", email);

      window.location.href = "dashboard.html";
    },
    onClose: function () {
      alert("Payment cancelled");
    }
  });

  handler.openIframe();
}
