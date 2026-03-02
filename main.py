import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai.errors import ClientError
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CHROMA_PATH = (
    BASE_DIR.parent.parent / "nitrochat-admin" / "nitrochat-admin-backend" / "rag-system" / "chroma"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
CHROMA_PATH = Path(os.getenv("CHROMA_PATH", str(DEFAULT_CHROMA_PATH))).resolve()
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "faq")
TOP_K = int(os.getenv("RAG_TOP_K", "4"))


class GeminiEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        response = self._client.models.embed_content(
            model=self._model_name,
            contents=list(input),
        )
        return [item.values for item in response.embeddings]


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: int = Field(default=TOP_K, ge=1, le=10)


class SourceItem(BaseModel):
    row_number: int | None = None
    category: str | None = None
    question: str | None = None
    answer: str | None = None
    filename: str | None = None
    source_file_id: str | None = None
    distance: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    retrieved_chunks: int


class RetrieveResponse(BaseModel):
    sources: list[SourceItem]
    retrieved_chunks: int


def require_api_key() -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")
    return GEMINI_API_KEY


def get_genai_client() -> genai.Client:
    return genai.Client(api_key=require_api_key())


def get_collection():
    if not CHROMA_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Chroma path does not exist: {CHROMA_PATH}",
        )

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_collection(
        name=CHROMA_COLLECTION,
        embedding_function=GeminiEmbeddingFunction(
            api_key=require_api_key(),
            model_name=GEMINI_EMBEDDING_MODEL,
        ),
    )


def retrieve_context(question: str, top_k: int) -> tuple[str, list[SourceItem]]:
    collection = get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "", []

    context_blocks: list[str] = []
    sources: list[SourceItem] = []

    for index, document in enumerate(documents, start=1):
        metadata: dict[str, Any] = metadatas[index - 1] or {}
        distance = distances[index - 1] if index - 1 < len(distances) else None
        context_blocks.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    document,
                    f"Metadata: {metadata}",
                ]
            )
        )
        sources.append(
            SourceItem(
                row_number=metadata.get("row_number"),
                category=metadata.get("category"),
                question=metadata.get("question"),
                answer=metadata.get("answer"),
                filename=metadata.get("filename"),
                source_file_id=metadata.get("source_file_id"),
                distance=distance,
            )
        )

    return "\n\n".join(context_blocks), sources


def build_prompt(message: str, history: list[ChatMessage], context: str) -> str:
    history_text = "\n".join(
        f"{item.role.upper()}: {item.content}"
        for item in history[-8:]
    )

    return (
        "You are a customer support chatbot for Nitro Chat.\n"
        "Answer only using the retrieved FAQ context when possible.\n"
        "If the answer is not in the context, say you do not have enough information.\n"
        "Be concise and practical.\n"
        "When relevant, mention the source number in square brackets like [Source 1].\n\n"
        f"Conversation history:\n{history_text or 'No prior history.'}\n\n"
        f"Retrieved FAQ context:\n{context or 'No relevant context found.'}\n\n"
        f"User question:\n{message}"
    )


def generate_answer(message: str, history: list[ChatMessage], context: str) -> str:
    client = get_genai_client()
    prompt = build_prompt(message=message, history=history, context=context)
    try:
        response = client.models.generate_content(
            model=GEMINI_CHAT_MODEL,
            contents=prompt,
        )
    except ClientError as exc:
        status_code = getattr(exc, "status_code", 502)
        if status_code == 429:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini quota exceeded for generation. "
                    "Check your API key, billing, or model quota."
                ),
            ) from exc
        raise HTTPException(
            status_code=502,
            detail=f"Gemini generation failed: {exc}",
        ) from exc
    return (response.text or "").strip()


app = FastAPI(title="NitroChat Customer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/rag/status")
def rag_status() -> dict[str, Any]:
    collection = get_collection()
    return {
        "collection": CHROMA_COLLECTION,
        "chroma_path": str(CHROMA_PATH),
        "document_count": collection.count(),
        "embedding_model": GEMINI_EMBEDDING_MODEL,
        "chat_model": GEMINI_CHAT_MODEL,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    context, sources = retrieve_context(payload.message, payload.top_k)
    answer = generate_answer(
        message=payload.message,
        history=payload.history,
        context=context,
    )

    if not answer:
        raise HTTPException(status_code=502, detail="Model returned an empty response")

    return ChatResponse(
        answer=answer,
        sources=sources,
        retrieved_chunks=len(sources),
    )


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(payload: ChatRequest) -> RetrieveResponse:
    _, sources = retrieve_context(payload.message, payload.top_k)
    return RetrieveResponse(
        sources=sources,
        retrieved_chunks=len(sources),
    )
