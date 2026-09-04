from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from config import RAZORPAY_KEY_ID
from cart import create_cart, add_item, get_cart, get_cart_total_price
from orders import (
    checkout,
    get_order_status,
    get_order,
    get_order_by_razorpay_id,
    update_order_status
)
from catalog import get_all_products, get_product_by_id
from models import OrderStatus
from razorpay_client import RazorpayClient


app = FastAPI(
    title="Merchant Commerce API",
    description="HTTP API for the merchant backend",
    version="1.0.0"
)

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int

class PaymentVerificationRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

@app.get("/products")
def get_products(
    query: str = "",
    max_price: float | None = None
):
    products = get_all_products()

    results = []

    for product in products:
        matches_query = (
            query.lower() in product.name.lower()
            or query.lower() in product.description.lower()
        )

        matches_price = (
            max_price is None
            or product.price <= max_price
        )

        if matches_query and matches_price:
            results.append(product.model_dump())

    return {
        "products": results
    }


@app.get("/products/{product_id}")
def get_product(product_id: str):
    product = get_product_by_id(product_id)

    if product is None:
        raise HTTPException(
        status_code=404,
        detail=f"Product '{product_id}' not found."
    )

    return product.model_dump()

@app.post("/carts")
def start_cart():
    cart = create_cart()

    return {
        "cart_id": cart.id,
        "items": []
    }

@app.post("/carts/{cart_id}/items")
def add_cart_item(
    cart_id: str,
    request: AddToCartRequest
):
    cart = add_item(
        cart_id,
        request.product_id,
        request.quantity
    )

    return {
        "cart_id": cart_id,
        "items": [
            item.model_dump()
            for item in cart.values()
        ],
        "total_amount": get_cart_total_price(cart)
    }

@app.get("/carts/{cart_id}")
def get_cart_api(cart_id: str):
    try:
        cart = get_cart(cart_id)

        return {
            "cart_id": cart_id,
            "items": [
                item.model_dump()
                for item in cart.values()
            ],
            "total_amount": get_cart_total_price(cart)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
@app.post("/checkout")
def checkout_cart(cart_id: str):
    return checkout(cart_id)

@app.get("/orders/{order_id}/status")
def get_order_status_api(order_id: str):
    try:
        return get_order_status(order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@app.get("/pay/{order_id}", response_class=HTMLResponse)
def payment_page(order_id: str):
    order = get_order(order_id)

    if order.status.value != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Order is not pending. Current status: {order.status.value}"
        )

    razorpay_order_id = order.razorpay_order_id
    amount_paise = int(round(order.total_amount * 100))

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Complete Payment</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    </head>

    <body>
        <h1>Complete Payment</h1>

        <p>Order ID: {order.id}</p>
        <p>Amount: ₹{order.total_amount}</p>

        <button id="pay-button">Pay with Razorpay</button>

        <script>
            const options = {{
                key: "{RAZORPAY_KEY_ID}",
                amount: {amount_paise},
                currency: "INR",
                name: "AI Buyer Merchant",
                description: "AI Buyer Agent Purchase",
                order_id: "{razorpay_order_id}",

                handler: async function (response) {{
                    console.log("Payment successful");
                    console.log(response);

                    const verificationResponse = await fetch("/payments/verify", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json"
                        }},
                        body: JSON.stringify({{
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_signature: response.razorpay_signature
                        }})
                    }});

                    const result = await verificationResponse.json();

                    if (!verificationResponse.ok) {{
                        alert("Payment verification failed: " + result.detail);
                        return;
                    }}


                    
        if (window.opener && !window.opener.closed) {{
                    window.opener.postMessage(
                        {{
                            type: "PAYMENT_SUCCESS",
                            orderId: result.order_id,
                            paymentId: result.razorpay_payment_id
                        }},
                        "http://127.0.0.1:9000"
                    );

                    // Close this payment tab.
                    window.close();
                            }}
        else {{
                window.location.href =
                    "http://127.0.0.1:9000/?payment=success" +
                    "&order_id=" + encodeURIComponent(result.order_id);
            }}

                }}
            }};

            const rzp = new Razorpay(options);

            document.getElementById("pay-button").onclick = function(e) {{
                rzp.open();
                e.preventDefault();
            }};
        </script>
    </body>
    </html>
    """

@app.post("/payments/verify")
def verify_payment(request: PaymentVerificationRequest):

    # 1. Find our local order
    try:
        order = get_order_by_razorpay_id(request.razorpay_order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    # 2. Verify that the Razorpay order belongs to our local order
    if order.razorpay_order_id != request.razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Razorpay order ID does not match local order."
        )

    # 3. Verify Razorpay signature
    razorpay_client = RazorpayClient()

    try:
        razorpay_client.verify_payment_signature(
            razorpay_order_id=order.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Payment signature verification failed."
        )

    # 4. Fetch the actual payment from Razorpay
    payment = razorpay_client.fetch_payment(
        request.razorpay_payment_id
    )

    if "error" in payment:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch payment from Razorpay."
        )

    # 5. Confirm the payment belongs to the expected Razorpay order
    if payment.get("order_id") != order.razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Payment does not belong to this order."
        )

    # 6. Confirm the amount
    expected_amount = int(round(order.total_amount * 100))

    if payment.get("amount") != expected_amount:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match order amount."
        )

    # 7. Confirm Razorpay says the payment is captured
    if payment.get("status") != "captured":
        raise HTTPException(
            status_code=400,
            detail=f"Payment is not captured. Status: {payment.get('status')}"
        )

    # 8. Only now mark our local order as PAID
    updated_order = update_order_status(
        order.id,
        OrderStatus.PAID
    )

    return {
        "success": True,
        "order_id": updated_order.id,
        "status": updated_order.status.value,
        "razorpay_payment_id": request.razorpay_payment_id
    }