// Function to pay for VIP
function payWithPaystack(email, plan) {
    // Amounts in kobo
    let amount = plan === 'weekly' ? 755000 : 2755000; // Weekly = ₦7,550, Monthly = ₦27,550

    let handler = PaystackPop.setup({
        key: 'pk_test_8f53865d8bded27a891f25b99bcdc15ccd9c6d6e', // 🔑 Replace with YOUR Paystack PUBLIC key
        email: email,
        amount: amount,
        currency: "NGN",
        callback: function(response) {
            // Payment successful → save VIP info with expiry
            let days = plan === 'weekly' ? 7 : 30;
            let expiry = new Date();
            expiry.setDate(expiry.getDate() + days);

            localStorage.setItem("vip_active", "true");
            localStorage.setItem("vip_expiry", expiry);

            // Redirect user to VIP page
            window.location.href = "vip.html";
        },
        onClose: function() {
            alert("Payment cancelled");
        }
    });

    handler.openIframe();
}
