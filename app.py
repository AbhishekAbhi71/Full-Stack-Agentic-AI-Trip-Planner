from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph.workflow import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

graph = build_graph()

class ChatRequest(BaseModel):
    message: str

def run_graph_stream(user_message: str):
    inputs = {
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    try:
        for chunk in graph.stream(
            inputs,
            stream_mode="custom",
            config={
                "recursion_limit": 30
            }
        ):
            if chunk:
                yield str(chunk)

    except Exception as e:
        print("❌ STREAM ERROR:", e)
        yield f"\n⚠️ Error: {str(e)}"

@app.post("/chat")
async def chat(request: ChatRequest):
    print("📩 User:", request.message)
    return StreamingResponse(
        run_graph_stream(request.message),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/")
async def home():
    return FileResponse(
        "frontend/index.html"
    )