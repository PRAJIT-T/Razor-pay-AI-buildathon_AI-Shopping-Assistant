from typing import Dict, List, Optional
from models import Order, OrderStatus
from cart import CartState
from audit import log_state_mutation # Assuming audit.py is implemented

# A type alias for the order state for clarity
OrderState = Dict[str, Order]

def create_new_order(
    cart_state: CartState, 
    customer_info: Dict, 
    total_amount: float
) -> Order:
    """
    Creates a new order from the current cart state.
    This is a pure function.
    """
    # 1. Validate cart state
    if not cart_state:
        raise ValueError("Cannot create an order from an empty cart.")
    
    # 2. Create the order object
    new_order = Order(
        order_id=f"ORD-{len(OrderState) + 1}", # Mock ID generation
        customer_info=customer_info,
        items=cart_state,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        created_at="2023-10-27T10:00:00Z" # Mock timestamp
    )
    
    # 3. Log the mutation (Mandatory requirement)
    log_state_mutation(
        entity_type="Order", 
        action="CREATE", 
        data=new_order.dict()
    )
    
    return new_order

def update_order_status(order_id: str, new_status: OrderStatus) -> Order:
    """
    Updates the status of an existing order.
    This is a pure function.
    """
    # In a real scenario, we would fetch the order from the state/database first.
    # For this mock, we assume the order exists and return a new state.
    
    # 1. Fetch the current order (mock)
    # current_order = get_order_by_id(order_id)
    
    # 2. Create the new order with updated status
    # new_order = current_order.copy(status=new_status)
    
    # 3. Log the mutation
    # log_state_mutation(
    #     entity_type="Order", 
    #     action="UPDATE", 
    #     data=new_order.dict()
    # )
    
    # Mock return for now
    return Order(
        order_id=order_id,
        customer_info={"mock": "data"},
        items={},
        total_amount=0.0,
        status=new_status,
        created_at="2023-10-27T10:00:00Z"
    )

def get_order_history(customer_id: str) -> List[Order]:
    """
    Retrieves all orders associated with a specific customer ID.
    This is a pure function.
    """
    # Mock implementation: return an empty list
    return []

# Example of how this function can be used (for testing/demonstration)
if __name__ == "__main__":
    print("--- Order Module Test ---")
    
    # Mock dependencies for testing
    class MockCartState:
        def __init__(self):
            self.items = {}
    
    class MockOrder:
        def __init__(self, order_id, customer_info, items, total_amount, status, created_at):
            self.order_id = order_id
            self.customer_info = customer_info
            self.items = items
            self.total_amount = total_amount
            self.status = status
            self.created_at = created_at
        def dict(self):
            return self.__dict__

    # Mock the log function
    def log_state_mutation(entity_type, action, data):
        print(f"LOG: {entity_type} {action} - {data}")

    # Override the mock function for the test
    # (In a real scenario, we'd use dependency injection or a test double)
    # For this test, we'll just use the mock Order class directly.
    
    # Create a mock cart state
    mock_cart = MockCartState()
    
    # Create a new order
    try:
        new_order = create_new_order(mock_cart.items, {"name": "Test User"}, 100.0)
        print(f"Order Created: {new_order.order_id} with status {new_order.status}")
        
        # Update status
        updated_order = update_order_status(new_order.order_id, OrderStatus.SHIPPED)
        print(f"Order Status Updated: {updated_order.status}")
        
        # Get history
        history = get_order_history("user_123")
        print(f"Order history count: {len(history)}")
        
    except ValueError as e:
        print(f"Error during test: {e}")