# AI Buyer Agent

An AI-powered agentic commerce system built for the Razorpay AI Buildathon — Track 01: AI Growth & Agentic Commerce.

The system allows a user to shop using natural language. The AI Buyer can discover products, maintain a shopping cart, prepare an order, request explicit user confirmation before checkout, initiate a Razorpay Test Mode payment, and rely on server-side verification before an order is marked as paid.

The design focuses on making every money action:

- Explainable
- Bounded
- Gated
- Verifiable
- Auditable

---

## Overview

Traditional e-commerce requires the user to manually search products, inspect details, manage a cart, and navigate through multiple checkout steps.

This project introduces an AI Buyer Agent that acts as the conversational layer over a merchant commerce system.

A user can interact with the system using natural language such as:

> I need wireless headphones under ₹1000

The AI searches the real merchant catalog through MCP, recommends suitable products, and maintains the conversation context.

The user can then say:

> Add that to my cart

The agent resolves the reference from the conversation and performs the cart operation.

When the user wants to purchase, the agent presents the final cart and total and requires explicit confirmation before initiating the payment flow.

---

## Key Features

### Natural Language Shopping

Users can describe what they want without knowing product IDs or backend APIs.

Examples:

- "Find wireless headphones under ₹1000"
- "Show me something cheaper"
- "Tell me more about that product"
- "Add that to my cart"
- "What's in my cart?"
- "Checkout"

The AI uses the merchant tools to obtain real catalog, cart, and order information rather than inventing values.

---

### Conversational Context

The Buyer Agent maintains conversation history and can resolve references such as:

- "that"
- "this product"
- "add it"
- "the second one"

This allows the shopping experience to remain conversational rather than requiring the user to repeatedly specify internal product identifiers.

---

### MCP-Based Tool Architecture

The AI does not directly manipulate the merchant system.

Instead, the Buyer Agent communicates with an MCP server that exposes controlled commerce operations.

Current MCP tools include:

- `search_catalog`
- `get_product_details`
- `start_cart`
- `add_to_cart`
- `get_cart`
- `checkout`
- `cancel_order`
- `get_audit_log`
- `get_order_status`

Read-only operations are separated conceptually from state-changing operations, and checkout is explicitly treated as the operation that initiates the payment process.

---

### Explicit Human Confirmation

The AI cannot directly initiate checkout simply because the user discussed a product.

Before checkout, the agent presents:

- Cart contents
- Quantities
- Total amount

The user must explicitly confirm before the checkout tool is called.

This provides a human authorization gate immediately before the money-related action.

---

### Spend Cap

The merchant backend enforces a configured spending limit.

If the checkout amount exceeds the configured spend cap, the checkout operation fails instead of allowing the payment flow to continue.

This provides a deterministic financial boundary independent of the AI's response.

---

### Razorpay Test Mode Integration

The system uses Razorpay Test Mode for the actual payment flow.

The checkout process is:

1. User confirms the final purchase.
2. Buyer Agent calls the MCP checkout tool.
3. MCP forwards the request to the merchant backend.
4. Merchant backend creates the local order.
5. Merchant backend creates a Razorpay payment order.
6. The user completes payment through Razorpay Checkout.
7. Razorpay returns the payment information.
8. The merchant backend verifies the payment server-side.
9. Only after successful verification is the local order marked `PAID`.

Creating a Razorpay order does not itself mean that the customer has paid.

---

## Server-Side Payment Verification

Payment verification is performed by the merchant backend rather than trusting the browser.

The verification process checks:

- The local order exists.
- The Razorpay order ID matches the expected order.
- The Razorpay payment signature is valid.
- The payment belongs to the expected Razorpay order.
- The payment amount matches the local order amount.
- The payment status is `captured`.

Only after all required checks succeed is the local order transitioned to:

```text
PAID
