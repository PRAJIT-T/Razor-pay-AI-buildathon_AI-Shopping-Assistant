from typing import Dict, List
from catalog import get_product_by_id
from datetime import datetime 
from models import Cart, CartItem
import uuid # Assuming models are in the same package structure

# A type alias for the cart state for clarity
CartState = Dict[str, CartItem]
_CARTS = {}

def create_cart() -> Cart:
    cart = create_empty_cart()
    _CARTS[cart.id] = {}
    return cart


def get_cart(cart_id: str) -> CartState:
    if cart_id not in _CARTS:
        raise ValueError(f"Cart '{cart_id}' not found.")
    return _CARTS[cart_id]



def create_empty_cart() -> Cart:
    return Cart(
        id=str(uuid.uuid4()) , 
        items={},
        total_amount=0.0,
        created_at=datetime.now()
        )

def add_item_to_cart(
    cart_state: CartState, 
    product_id: str, 
    quantity: int
) -> CartState:
    
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    
    # Get the product details to ensure it's a valid product (optional validation)
    # In a real scenario, we'd call catalog.get_product_by_id(product_id) here.
    # For now, we assume the ID is valid.
    
    product = get_product_by_id(product_id)

    if product is None:
        raise ValueError(f"product {product_id} not found")

    new_cart_state = cart_state.copy()
    
    if product_id in new_cart_state:
        # Update existing item
        new_cart_state[product_id] = CartItem(
            product_id=product_id, 
            quantity=new_cart_state[product_id].quantity + quantity,
            price=product.price
        )
    else:
        # Add new item
        # Note: We don't have the full Product object here, so we just store the ID and quantity
        new_cart_state[product_id] = CartItem(
            product_id=product_id, 
            quantity=quantity,
            price=product.price
        )
    return new_cart_state

def add_item(cart_id: str, product_id: str, quantity: int) -> CartState:
    cart_state = get_cart(cart_id)

    new_cart_state = add_item_to_cart(
        cart_state,
        product_id,
        quantity
    )

    _CARTS[cart_id] = new_cart_state

    return new_cart_state

def remove_item_from_cart(cart_state: CartState, product_id: str) -> CartState:
    """
    Removes a product from the cart by its ID.
    This is a pure function that returns a new cart state.
    """
    if product_id not in cart_state:
        return cart_state # Item not found, return original state
    
    new_cart_state = cart_state.copy()
    del new_cart_state[product_id]
    return new_cart_state

def get_cart_total_price(cart_state: CartState) -> float:
    """
    Calculates the total price of all items in the cart.
    This is a pure function.
    """
    total = 0.0

    for item in cart_state.values():
        total+= item.price * item.quantity
    return total

def get_cart_items(cart_state: CartState) -> List[CartItem]:
    """
    Returns a list of all CartItem objects currently in the cart.
    This is a pure function.
    """
    return list(cart_state.values())

# Example of how this function can be used (for testing/demonstration)
if __name__ == "__main__":
    # This block requires the models.py to be available in the same directory
    # and the imports to work.
    print("--- Cart Module Test ---")
    
    # Create an empty cart
    initial_cart = create_empty_cart()
    print(f"Initial Cart: {initial_cart.items}")
    
    # Add items
    cart_after_add = add_item_to_cart(initial_cart.items, "prod_001", 2)
    print(f"Cart after adding prod_001: {cart_after_add}")
    
    # Add another item
    cart_after_add_2 = add_item_to_cart(cart_after_add, "prod_002", 1)
    print(f"Cart after adding prod_002: {cart_after_add_2}")
    
    # Remove an item
    cart_after_remove = remove_item_from_cart(cart_after_add_2, "prod_001")
    print(f"Cart after removing prod_001: {cart_after_remove}")
    
    # Get items
    items = get_cart_items(cart_after_remove)
    print(f"Items in cart: {items}")
    
    # Calculate total (will be 0.0 in this mock setup)
    total = get_cart_total_price(cart_after_remove)
    print(f"Total price: ${total}")