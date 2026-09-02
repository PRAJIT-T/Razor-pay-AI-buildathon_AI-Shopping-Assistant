import os
import razorpay
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

class RazorpayClient:
    """
    A client to interact with the Razorpay payment gateway.
    This class encapsulates all external API calls.
    """
    def __init__(self):
        """
        Initializes the Razorpay client with API keys.
        """
        self.client = razorpay.Client(
            key_id=RAZORPAY_KEY_ID,
            key_secret=RAZORPAY_KEY_SECRET
        )

    def create_order(self, amount: float, currency: str = "INR") -> dict:
        """
        Creates a new order on Razorpay.

        Args:
            amount: The amount to charge in the smallest currency unit (e.g., paise for INR).
            currency: The currency code (e.g., "INR").

        Returns:
            A dictionary containing the order details from Razorpay.
        """
        try:
            order = self.client.order.create(
                amount=amount,
                currency=currency,
                receipt="order_receipt_id" # Placeholder for a unique receipt ID
            )
            return order
        except Exception as e:
            print(f"Error creating Razorpay order: {e}")
            return {"error": str(e)}

    def verify_payment(self, payment_id: str) -> dict:
        """
        Verifies a payment using its ID.

        Args:
            payment_id: The ID of the payment to verify.

        Returns:
            A dictionary containing the payment details.
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return {"error": str(e)}

# Example usage (for testing purposes, not part of the final module)
if __name__ == "__main__":
    # NOTE: This block will fail unless RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set in the environment
    # and a valid API key is used.
    print("--- Razorpay Client Test ---")
    try:
        client = RazorpayClient()
        # Mock amount for testing
        test_amount = 10000 # 100 INR
        print(f"Attempting to create a test order for {test_amount} paise...")
        # order_data = client.create_order(test_amount)
        # print("Order created successfully (mock):", order_data)
    except Exception as e:
        print(f"Could not initialize client: {e}")
        print("Please ensure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set in config.py or environment variables.")