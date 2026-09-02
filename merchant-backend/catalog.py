import json
import os
from typing import List
from models import Product 

# Define the path to the catalog file
CATALOG_PATH = os.path.join(
    os.path.dirname(__file__), 
    "data", 
    "catalog.json"
)

def get_all_products() -> List[Product]:
    """
    Reads the product catalog from the JSON file and returns a list of all products.
    This function is a pure function and does not modify any external state.
    """
    try:
        with open(CATALOG_PATH, 'r') as f:
            data = json.load(f)
            # Assuming the JSON structure is a list of product objects
            return [Product(**item) for item in data]
    except FileNotFoundError:
        print(f"Error: Catalog file not found at {CATALOG_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {CATALOG_PATH}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading the catalog: {e}")
        return []

def get_product_by_id(product_id: str) -> Product | None:
    """
    Retrieves a single product by its ID from the catalog.
    """
    products = get_all_products()
    for product in products:
        if product.id == product_id:
            return product
    return None

def get_products_by_price_range(min_price: float, max_price: float) -> List[Product]:
    """
    Filters products within a specified price range.
    """
    products = get_all_products()
    return [p for p in products if min_price <= p.price <= max_price]

# Example of how this function can be used (for testing/demonstration)
if __name__ == "__main__":
    print("--- All Products ---")
    products = get_all_products()
    for product in products:
        print(f"ID: {product.id}, Name: {product.name}, Price: ${product.price}")

    print("\n--- Products between $100 and $350 ---")
    filtered_products = get_products_by_price_range(100.0, 350.0)
    for product in filtered_products:
        print(f"ID: {product.id}, Name: {product.name}, Price: ${product.price}")