import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent       # extrator-imoveis/
_REPO_ROOT = _ROOT.parent                             # repo root (has vision/)
for _path in (_ROOT, _REPO_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from core.service import process_property
from core.vision_client import VisionExtractionError

app = FastAPI()

# TODO: consider validating Telegram initData for stronger auth
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_HTML = Path(__file__).resolve().parent / "index.html"

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


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

    for img in images:
        if img.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Formato inválido. Use PNG, JPG ou WebP",
            )

    payload = [(await img.read(), img.content_type or "image/png") for img in images]

    try:
        result = await run_in_threadpool(process_property, payload)
    except VisionExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"result": result}
