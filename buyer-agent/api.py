from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import BuyerAgent


buyer = BuyerAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting AI Buyer...")

    await buyer.start()

    print("AI Buyer started successfully.")

    yield

    print("Stopping AI Buyer...")

    await buyer.stop()

    print("AI Buyer stopped.")


app = FastAPI(
    title="AI Buyer API",
    description="AI shopping agent powered by Gemma and MCP",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
def frontend():
    return FileResponse("static/index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:
        response = await buyer.chat(request.message)

        return ChatResponse(
            response=response
        )

    except Exception as e:
        print(f"Chat error: {e}")

        raise HTTPException(
            status_code=500,
            detail="AI Buyer failed to process the request."
        )