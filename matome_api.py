from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/gerar-pdf")
def gerar_pdf(dados: dict):
    return {"message": "teste"}
