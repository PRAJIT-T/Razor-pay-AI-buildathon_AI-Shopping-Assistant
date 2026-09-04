from flask import Flask, request, render_template_string

from config import RAZORPAY_KEY_ID


app = Flask(__name__)


CHECKOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Razorpay Test Payment</title>
</head>

<body>

    <h2>Razorpay Test Payment</h2>

    <p>Local Order: {{ local_order_id }}</p>
    <p>Amount: ₹{{ amount_rupees }}</p>

    <button id="pay-button">Pay with Razorpay</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

    <script>
        const options = {
            key: "{{ razorpay_key_id }}",
            amount: "{{ amount_paise }}",
            currency: "INR",
            name: "Agent Commerce Demo",
            description: "Razorpay AI Buildathon Test Payment",
            order_id: "{{ razorpay_order_id }}",

            handler: function (response) {

                console.log("Payment successful");
                console.log(response);

                document.body.innerHTML = `
                    <h2>Payment completed on Razorpay</h2>

                    <p>Payment ID: ${response.razorpay_payment_id}</p>
                    <p>Razorpay Order ID: ${response.razorpay_order_id}</p>

                    <p>
                        Payment has NOT yet been verified by the merchant backend.
                    </p>
                `;
            }
        };

        const razorpay = new Razorpay(options);

        document.getElementById("pay-button").onclick = function (event) {
            razorpay.open();
            event.preventDefault();
        };
    </script>

</body>
</html>
"""


@app.route("/pay")
def pay():

    local_order_id = request.args.get("local_order_id")
    razorpay_order_id = request.args.get("razorpay_order_id")
    amount_paise = request.args.get("amount")

    if not local_order_id or not razorpay_order_id or not amount_paise:
        return "Missing payment information.", 400

    amount_rupees = int(amount_paise) / 100

    return render_template_string(
        CHECKOUT_PAGE,
        razorpay_key_id=RAZORPAY_KEY_ID,
        local_order_id=local_order_id,
        razorpay_order_id=razorpay_order_id,
        amount_paise=amount_paise,
        amount_rupees=amount_rupees
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)