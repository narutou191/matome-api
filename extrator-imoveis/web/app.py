from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from core.service import process_property
from core.vision_client import VisionExtractionError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_HTML = Path(__file__).resolve().parent / "index.html"


@app.get("/")
def serve_index():
    return FileResponse(INDEX_HTML)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process(images: list[UploadFile] = File(...)):
    if len(images) != 2:
        raise HTTPException(
            status_code=400,
            detail="Envie as 2 capturas de tela (物件概要 e その他詳細)",
        )

    payload = [(await img.read(), img.content_type or "image/png") for img in images]

    try:
        result = await run_in_threadpool(process_property, payload)
    except VisionExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"result": result}
