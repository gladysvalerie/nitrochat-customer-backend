from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chat import router as chat_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173","http://localhost:5175", 
        "http://s00gk4088k44o480ws8ckog8.213.35.118.103.sslip.io",
        "http://ug8480s0o44g0g0c80ccc8o0.213.35.118.103.sslip.io"
        ], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/health")
async def health():
    return {"ok": True}

app.include_router(chat_router, prefix="/api/customer")

# For fastAPI coolify integration
if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)