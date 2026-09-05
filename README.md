# AI Shopping Agent

An AI-powered agentic commerce system built for the **Razorpay AI Buildathon — Track 01: AI Growth & Agentic Commerce**.

The system allows users to shop using natural language. The AI Buyer can discover products, maintain a shopping cart, prepare an order, request explicit user confirmation before checkout, initiate a Razorpay Test Mode payment, and rely on server-side verification before an order is marked as paid.

The design focuses on making every money action:

- Explainable
- Bounded
- Gated
- Verifiable
- Auditable

---

## Overview

Traditional e-commerce requires users to manually search for products, inspect details, manage a cart, and navigate through multiple checkout steps.

This project introduces an **AI Buyer Agent** that acts as a conversational layer over a merchant commerce system.

A user can interact with the system using natural language:

> I need wireless headphones under ₹1000

The AI searches the real merchant catalog through MCP, recommends suitable products, and maintains conversation context.

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

The AI uses merchant tools to obtain real catalog, cart, and order information rather than inventing values.

### Conversational Context

The Buyer Agent maintains conversation history and can resolve references such as:

- "that"
- "this product"
- "add it"
- "the second one"

This allows the shopping experience to remain conversational without requiring users to repeatedly provide internal product identifiers.

### MCP-Based Tool Architecture

The AI does not directly manipulate the merchant system.

Instead, the Buyer Agent communicates with an **MCP server**, which exposes controlled commerce operations.

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

The MCP layer provides a controlled boundary between the AI agent and the merchant backend.

### Explicit Human Confirmation

Checkout requires an explicit human confirmation.

Before calling the checkout operation, the agent presents:

- Final cart contents
- Quantities
- Total amount

The user must explicitly confirm before the payment flow is initiated.

### Spend Cap

The merchant backend enforces a configured spending limit.

If the checkout amount exceeds the configured spend cap, checkout fails instead of allowing the payment process to continue.

This provides a deterministic financial boundary independent of the AI's response.

### Razorpay Test Mode

The project integrates **Razorpay Test Mode** for the payment flow.

The process is:

1. User confirms the final purchase.
2. Buyer Agent calls the MCP checkout tool.
3. MCP forwards the request to the merchant backend.
4. Merchant backend creates the local order.
5. Merchant backend creates a Razorpay payment order.
6. The user completes payment through Razorpay Checkout.
7. Payment information is returned to the merchant backend.
8. The merchant backend verifies the payment server-side.
9. Only after successful verification is the local order marked `PAID`.

Creating a Razorpay order does **not** mean that the customer has paid.

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

Only after these checks succeed is the local order transitioned to:

```text
PAID

Order Lifecycle

Orders use controlled states to ensure that payment and order status remain consistent.

PENDING
   |
   | Successful server-side payment verification
   v
PAID

Pending orders can also be cancelled:

PENDING
   |
   | Cancellation
   v
CANCELLED

Cancellation is intentionally restricted to unpaid pending orders.

A paid order is not cancelled through this operation because a paid order would require a separate refund workflow.

Audit Trail

The merchant backend maintains an audit trail of state-changing operations.

The audit log records:

Timestamp
Entity
Action
Associated data

Examples include:

Order created
Razorpay order created
Order updated -> PAID
Order cancelled

The audit log can be retrieved through the merchant API and exposed to the AI through the get_audit_log MCP tool.

This provides traceability for important commerce and payment state transitions.

System Architecture
                         USER
                           |
                           v
                  +----------------+
                  |   AI Buyer UI  |
                  | Browser / Chat |
                  +----------------+
                           |
                           v
                  +----------------+
                  | buyer-agent    |
                  |    api.py      |
                  |    :9000       |
                  +----------------+
                           |
                           v
                  +----------------+
                  |  Buyer Agent   |
                  |  Local Gemma   |
                  +----------------+
                           |
                           | MCP
                           v
                  +----------------+
                  |   MCP Server   |
                  |    server.py   |
                  +----------------+
                           |
                           | HTTP
                           v
                  +----------------+
                  | Merchant       |
                  | Backend :8000  |
                  +----------------+
                    /      |       \
                   /       |        \
                  v        v         v
             Catalog     Cart      Orders
                                      |
                                      v
                                    Audit
                                      |
                                      v
                              Razorpay Client
                                      |
                                      v
                              Razorpay Test Mode
                                      |
                                      v
                              Razorpay Checkout
                                      |
                                      v
                           Server-side Verification
                                      |
                                      v
                                 Order -> PAID
Project Structure
AI-Buyer-Agent/
│
├── buyer-agent/
│   ├── api.py
│   ├── agent.py
│   │
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
│
├── mcp-server/
│   └── server.py
│
├── merchant-backend/
│   ├── api.py
│   ├── audit.py
│   ├── cart.py
│   ├── catalog.py
│   ├── config.py
│   ├── models.py
│   ├── orders.py
│   ├── razorpay_client.py
│   │
│   └── data/
│       └── catalog.json
│
├── .env
├── .gitignore
└── README.md
