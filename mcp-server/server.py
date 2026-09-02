import sys
import os
import asyncio
import json
from typing import Any

# ---------------------------------------------------------
# Allow MCP server to import the existing merchant backend
# ---------------------------------------------------------

BACKEND_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "merchant-backend")
)

if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)


# ---------------------------------------------------------
# MCP imports
# ---------------------------------------------------------

import mcp.server.stdio
import mcp.types as types

from mcp.server.lowlevel import Server
from mcp.server.context import ServerRequestContext


# ---------------------------------------------------------
# Merchant backend imports
# ---------------------------------------------------------

from catalog import get_all_products, get_product_by_id
from cart import create_cart, add_item
from orders import checkout, get_order_status


# ---------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------

TOOLS = [

    types.Tool(
        name="search_catalog",
        description=(
            "Search the merchant product catalog. "
            "This is a read-only operation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name or description to search for."
                },
                "max_price": {
                    "type": "number",
                    "description": "Optional maximum product price."
                },
                "size": {
                    "type": "string",
                    "description": (
                        "Optional size filter. "
                        "The current merchant catalog does not contain size data."
                    )
                }
            },
            "required": ["query"]
        }
    ),

    types.Tool(
        name="get_product_details",
        description=(
            "Get detailed information about a specific product. "
            "This is a read-only operation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The product ID."
                }
            },
            "required": ["product_id"]
        }
    ),

    types.Tool(
        name="start_cart",
        description=(
            "Create a new empty shopping cart. "
            "This does not spend money."
        ),
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),

    types.Tool(
        name="add_to_cart",
        description=(
            "Add a product to an existing shopping cart. "
            "This does not spend money."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": "The shopping cart ID."
                },
                "product_id": {
                    "type": "string",
                    "description": "The product ID."
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of units to add."
                }
            },
            "required": [
                "cart_id",
                "product_id",
                "quantity"
            ]
        }
    ),

    types.Tool(
        name="checkout",
        description=(
            "Checkout the shopping cart and create a Razorpay payment order. "
            "THIS IS THE ONLY TOOL THAT INITIATES THE PAYMENT FLOW. "
            "It must only be called after the user has explicitly confirmed "
            "the final cart contents and total amount. "
            "The merchant SpendCap is enforced. "
            "If the SpendCap is exceeded, checkout fails. "
            "Successful Razorpay order creation does NOT mean the customer "
            "has paid; it only creates the Razorpay payment order."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": "The cart to checkout."
                }
            },
            "required": ["cart_id"]
        }
    ),

    types.Tool(
        name="get_order_status",
        description=(
            "Get the current status of an order. "
            "This is a read-only operation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID."
                }
            },
            "required": ["order_id"]
        }
    )
]


# ---------------------------------------------------------
# List tools handler
# ---------------------------------------------------------

async def handle_list_tools(
    ctx: ServerRequestContext[Any],
    params: types.PaginatedRequestParams | None
) -> types.ListToolsResult:

    return types.ListToolsResult(
        tools=TOOLS
    )


# ---------------------------------------------------------
# Call tool handler
# ---------------------------------------------------------

async def handle_call_tool(
    ctx: ServerRequestContext[Any],
    params: types.CallToolRequestParams
) -> types.CallToolResult:

    try:

        arguments = params.arguments or {}

        # ---------------------------------------------
        # SEARCH CATALOG
        # ---------------------------------------------

        if params.name == "search_catalog":

            query = arguments.get("query", "")
            max_price = arguments.get("max_price")

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

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(results, default=str)
                    )
                ]
            )


        # ---------------------------------------------
        # GET PRODUCT DETAILS
        # ---------------------------------------------

        elif params.name == "get_product_details":

            product_id = arguments["product_id"]

            product = get_product_by_id(product_id)

            if product is None:

                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"Product '{product_id}' not found."
                            })
                        )
                    ],
                    is_error=True
                )

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            product.model_dump(),
                            default=str
                        )
                    )
                ]
            )


        # ---------------------------------------------
        # START CART
        # ---------------------------------------------

        elif params.name == "start_cart":

            cart = create_cart()

            result = {
                "cart_id": cart.id,
                "items": []
            }

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result)
                    )
                ]
            )


        # ---------------------------------------------
        # ADD TO CART
        # ---------------------------------------------

        elif params.name == "add_to_cart":

            cart_id = arguments["cart_id"]
            product_id = arguments["product_id"]
            quantity = arguments["quantity"]

            cart = add_item(
                cart_id,
                product_id,
                quantity
            )

            result = {
                "cart_id": cart_id,
                "items": [
                    item.model_dump()
                    for item in cart.values()
                ]
            }

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, default=str)
                    )
                ]
            )


        # ---------------------------------------------
        # CHECKOUT
        # ---------------------------------------------

        elif params.name == "checkout":

            cart_id = arguments["cart_id"]

            result = checkout(cart_id)

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, default=str)
                    )
                ]
            )


        # ---------------------------------------------
        # ORDER STATUS
        # ---------------------------------------------

        elif params.name == "get_order_status":

            order_id = arguments["order_id"]

            result = get_order_status(order_id)

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, default=str)
                    )
                ]
            )


        # ---------------------------------------------
        # UNKNOWN TOOL
        # ---------------------------------------------

        else:

            raise ValueError(
                f"Unknown tool: {params.name}"
            )


    except Exception as e:

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e)
                    })
                )
            ],
            is_error=True
        )


# ---------------------------------------------------------
# Create MCP server
# ---------------------------------------------------------

server = Server(
    "merchant-commerce",
    on_list_tools=handle_list_tools,
    on_call_tool=handle_call_tool
)


# ---------------------------------------------------------
# Run server using stdio
# ---------------------------------------------------------

async def main():

    async with mcp.server.stdio.stdio_server() as (
        read_stream,
        write_stream
    ):

        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())