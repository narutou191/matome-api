from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import logging
from matome_pdf_generator import gerar_pdf_matome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MATOME PDF API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DadosSimulacao(BaseModel):
    nome: str = ""
    idade: str = ""
    data: str = ""
    fin: int = 0
    car: int = 0
    crt: int = 0
    luz: int = 0
    gas: int = 0
    out: int = 0
    out2: int = 0
    pmt_a: int = 0
    pmt_b: int = 0
    eco_mensal: int = 0
    anos_a: int = 35
    taxa_a: float = 2.84
    anos_b: int = 10
    taxa_b: float = 3.29
    total_a: int = 0
    total_b: int = 0

@app.post("/api/gerar-pdf")
async def gerar_pdf(dados: DadosSimulacao):
    try:
        logger.info(f"Gerando PDF para: {dados.nome or 'simulacao'}")
        dados_dict = dados.dict()
        pdf_bytes = gerar_pdf_matome(dados_dict)
        nome_arquivo = f"MATOME-{(dados.nome or 'simulacao').replace(' ', '_')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
