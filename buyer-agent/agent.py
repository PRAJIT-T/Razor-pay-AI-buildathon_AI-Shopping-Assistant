import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    SQLiteSession,
    set_tracing_disabled,
)

from agents.mcp import MCPServerStdio


# Our model is local, so OpenAI tracing is unnecessary.
set_tracing_disabled(True)


async def main():

    # Connect to llama.cpp's OpenAI-compatible API
    client = AsyncOpenAI(
        base_url="http://127.0.0.1:9931/v1",
        api_key="local",
    )

    session = SQLiteSession("buyer_demo")

    # Connect to our existing MCP server
    async with MCPServerStdio(
        name="Merchant MCP Server",
        params={
            "command": "python",
            "args": [
                "../mcp-server/server.py"
            ],
        },
    ) as mcp_server:

        agent = Agent(
            name="AI Buyer",

            instructions="""
You are an AI shopping assistant.

Your job is to help the user find products and manage their shopping cart
using the available merchant MCP tools.

Rules:
- Use the MCP tools to obtain real product and cart information.
- Never invent products, prices, stock, cart contents, or order statuses.
- Before calling checkout, clearly tell the user the final cart contents
  and total amount and obtain explicit confirmation.
- Never claim that an order is paid unless the merchant system reports it
  as paid.
""",

            model=OpenAIChatCompletionsModel(
                model="D:\\models\\gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf",
                openai_client=client,
            ),

            mcp_servers=[mcp_server],
        )

        while True:
            user_message = input("\nYou: ")

            if user_message.lower() in ["exit", "quit"]:
                break

            result = await Runner.run(
                agent,
                user_message,
                session=session
            )

            print("\nAI:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())