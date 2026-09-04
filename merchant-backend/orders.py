from typing import Dict, List
from datetime import datetime 
import uuid
from config import SPEND_CAP
from razorpay_client import RazorpayClient
from models import Order, OrderStatus , CartItem
from cart import CartState , get_cart_total_price
from audit import log_state_mutation # Assuming audit.py is implemented

_ORDERS = {}

def create_new_order(
    cart_state: CartState, 
    customer_info: Dict, 
    total_amount: float
) -> Order:
    """
    Creates a new order from the current cart state.
    This is a pure function.
    """
    now = datetime.now()
    # 1. Validate cart state
    if not cart_state:
        raise ValueError("Cannot create an order from an empty cart.")
    
    # 2. Create the order object
    new_order = Order(
        id=f"ORD-{uuid.uuid4().hex[:8]}", # Mock ID generation
        customer_id=customer_info["customer_id"],
        items=list(cart_state.values()),
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        created_at=now,
        updated_at=now 
    )
    
    # 3. Log the mutation (Mandatory requirement)
    log_state_mutation(
        entity_type="Order", 
        action="CREATE", 
        data=new_order.model_dump()
    )

    _ORDERS[new_order.id] = new_order
    return new_order

def get_order(order_id: str) -> Order:
    if order_id not in _ORDERS:
        raise ValueError(f"Order '{order_id}' not found.")

    return _ORDERS[order_id]

def get_order_by_razorpay_id(razorpay_order_id: str) -> Order:
    for order in _ORDERS.values():
        if order.razorpay_order_id == razorpay_order_id:
            return order

    raise ValueError(
        f"Order with Razorpay order ID '{razorpay_order_id}' not found."
    )


def get_order_status(order_id: str) -> dict:
    if order_id not in _ORDERS:
        raise ValueError(f"Order '{order_id}' not found.")

    order = _ORDERS[order_id]

    return {
        "order_id": order.id,
        "status": order.status.value,
        "razorpay_order_id": order.razorpay_order_id
    }


def update_order_status(
    order_id: str,
    new_status: OrderStatus
) -> Order:

    if order_id not in _ORDERS:
        raise ValueError(f"Order '{order_id}' not found.")

    order = _ORDERS[order_id]

    order.status = new_status
    order.updated_at = datetime.now()

    log_state_mutation(
        entity_type="Order",
        action="UPDATE",
        data=order.model_dump()
    )

    return order

def get_order_history(customer_id: str) -> List[Order]:
    """
    Retrieves all orders associated with a specific customer ID.
    This is a pure function.
    """
    # Mock implementation: return an empty list
    return []

def checkout(cart_id: str) -> dict:
    from cart import get_cart

    cart_state = get_cart(cart_id)

    if not cart_state:
        raise ValueError("Cannot checkout an empty cart.")

    total_amount = get_cart_total_price(cart_state)

    if total_amount > SPEND_CAP:
        raise ValueError(
            f"Order total {total_amount} exceeds spend cap {SPEND_CAP}"
        )

    try:
        # 1. Create local order
        new_order = create_new_order(
            cart_state,
            {"customer_id": "buyer_agent"},
            total_amount
        )

        # 2. Convert INR to paise for Razorpay
        razorpay_amount = int(round(total_amount * 100))

        # 3. Create Razorpay order
        razorpay_client = RazorpayClient()

        razorpay_order = razorpay_client.create_order(
            razorpay_amount
        )

        if "error" in razorpay_order:
            raise ValueError(
                f"Razorpay order creation failed: "
                f"{razorpay_order['error']}"
            )

        # 4. Attach Razorpay order ID to local order
        new_order.razorpay_order_id = razorpay_order["id"]

        # 5. Audit successful Razorpay order creation
        log_state_mutation(
            entity_type="PaymentOrder",
            action="RAZORPAY_ORDER_CREATED",
            data=razorpay_order
        )

        # 6. Return both local and Razorpay order details
        return {
            "order": new_order.model_dump(),
            "razorpay_order": razorpay_order
        }

    except Exception as e:
        print(f"Checkout failed due to an internal error: {e}")
        return {
            "error": str(e),
            "status": "FAILED"
        }


# Example of how this function can be used (for testing/demonstration)
if __name__ == "__main__":
    print("--- Order Module Test ---")
    
    
    mock_cart = {
    "prod_001": CartItem(
        product_id="prod_001",
        quantity=1,
        price=299.99
    )
}
    
    # Create a new order
    try:
        new_order = create_new_order(mock_cart, {"customer_id": "User_123"}, 299.99)
        print(f"Order Created: {new_order.id} with status {new_order.status}")
        
        # Update status
        updated_order = update_order_status(new_order.id, OrderStatus.SHIPPED)
        print(f"Order Status Updated: {updated_order.status}")
        
        # Get history
        history = get_order_history("user_123")
        print(f"Order history count: {len(history)}")
        
    except ValueError as e:
        print(f"Error during test: {e}")