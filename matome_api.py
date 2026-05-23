from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from matome_pdf_generator import gerar_pdf_matome

app = FastAPI()

# Enable CORS for all origins
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
def gerar_pdf(dados: DadosSimulacao):
    """Gera PDF MATOME a partir dos dados da simulação"""
    try:
        # Convert Pydantic model to dict
        dados_dict = dados.model_dump()

        # Generate PDF
        pdf_bytes = gerar_pdf_matome(dados_dict)

        # Return as PDF file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=simulacao_matome.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/health")
def health():
    return {"status": "ok"}
