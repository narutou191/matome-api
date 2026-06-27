from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import asyncio
from geocode import resolver_cep
from hazardmap import gerar_pdf_hazardmap
from comprovante import gerar_comprovante


app = FastAPI(title="ハザードマップ API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Create pdfs directory
os.makedirs("pdfs", exist_ok=True)

# Risk type mapping
TIPOS = {
    "1": "洪水ハザードマップ",
    "2": "内水ハザードマップ",
    "3": "高潮ハザードマップ",
    "4": "津波ハザードマップ",
    "5": "土砂災害ハザードマップ",
}


class ConsultaRequest(BaseModel):
    cep: str
    tipo: str = "1"
    corretor: str = ""


@app.get("/")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "ハザードマップ API"}


@app.post("/gerar-pdf")
async def gerar_pdf(req: ConsultaRequest):
    """
    Generate hazard map PDF and proof-of-consultation.

    Input:
        - cep: 7-digit Japanese CEP (e.g. "5191424")
        - tipo: Risk type "1"-"5"
        - corretor: Optional realtor name

    Output:
        - JSON with links to download PDFs
    """
    # Validate CEP
    cep = req.cep.replace("-", "").strip()
    if len(cep) != 7 or not cep.isdigit():
        raise HTTPException(
            status_code=400,
            detail="CEP inválido. Use formato: 5191424 (7 dígitos)"
        )

    # Validate risk type
    if req.tipo not in TIPOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Use um de: {', '.join(TIPOS.keys())}"
        )

    try:
        # Step 1: Resolve CEP to coordinates
        endereco = await resolver_cep(cep)

        # Step 2: Generate unique filenames
        unique_id = str(uuid.uuid4())[:8]
        nome_mapa = f"{unique_id}.pdf"
        nome_comp = f"comp_{unique_id}.pdf"
        caminho_mapa = f"pdfs/{nome_mapa}"
        caminho_comp = f"pdfs/{nome_comp}"

        # Step 3: Generate hazard map PDF
        await gerar_pdf_hazardmap(
            lat=endereco["lat"],
            lon=endereco["lon"],
            tipo=req.tipo,
            output_path=caminho_mapa,
        )

        # Step 4: Generate proof-of-consultation PDF
        gerar_comprovante(
            dados={
                "cep": f"〒{cep[:3]}-{cep[3:]}",
                "prefeitura": endereco["address1"],
                "municipio": endereco["address2"],
                "bairro": endereco["address3"],
                "tipo": TIPOS[req.tipo],
                "corretor": req.corretor,
                "url_fonte": "https://disaportal.gsi.go.jp",
            },
            output_path=caminho_comp,
        )

        # Step 5: Build response URLs
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        return {
            "status": "success",
            "endereco": {
                "cep": f"〒{cep[:3]}-{cep[3:]}",
                "prefeitura": endereco["address1"],
                "municipio": endereco["address2"],
                "bairro": endereco["address3"],
            },
            "tipo": TIPOS[req.tipo],
            "downloads": {
                "mapa_pdf": f"{base_url}/download/{nome_mapa}",
                "comprovante": f"{base_url}/download/{nome_comp}",
            },
        }

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao resolver CEP: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar PDF: {str(e)}"
        )


@app.get("/download/{filename}")
def download(filename: str):
    """Download a generated PDF"""
    # Security: only allow downloads from pdfs/ directory
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Filename inválido")

    caminho = f"pdfs/{filename}"
    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado"
        )

    return FileResponse(
        caminho,
        media_type="application/pdf",
        filename=filename,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
