# API MATOME — Gerador de PDF

## Instalação

### 1. Instalar dependências

```bash
pip install fastapi uvicorn reportlab pydantic
```

### 2. Rodar a API

```bash
python matome_api.py
```

A API estará rodando em: **http://localhost:8000**

## Verificar se está funcionando

```bash
curl http://localhost:8000/health
```

Deve retornar: `{"status":"ok"}`

## Como funciona

1. **Frontend (HTML)** — Coleta dados da simulação e envia para a API via POST
2. **API (FastAPI)** — Recebe dados e chama o gerador de PDF
3. **Gerador (reportlab)** — Cria um PDF profissional e retorna para download

### Endpoints

#### POST `/api/gerar-pdf`
Gera PDF da simulação MATOME

**Body (JSON):**
```json
{
  "nome": "Yamamoto Hiroshi",
  "idade": "41",
  "data": "23/05/2026",
  "fin": 90000,
  "car": 30000,
  "crt": 0,
  "luz": 20000,
  "gas": 15000,
  "out": 15000,
  "out2": 0,
  "ref": 0,
  "ext": 0,
  "sol": 0,
  "oob": 0,
  "pmt_a": 65206,
  "pmt_b": 11938,
  "eco_mensal": 77856,
  "anos_a": 35,
  "taxa_a": 1.74,
  "anos_b": 35,
  "taxa_b": 2.19,
  "total_a": 20500000,
  "total_b": 3500000
}
```

**Retorna:** PDF como arquivo para download

#### GET `/health`
Health check

**Retorna:** `{"status":"ok"}`

---

## Testar localmente

Execute o script de teste:

```bash
python matome_pdf_generator.py
```

Isso gerará um PDF de teste em `C:\Users\hiros\Downloads\test_matome.pdf`

---

## Deployment em Produção

Para rodar em casapropriajp.com, você precisa:

1. Hospedar a API no servidor (ou em outro servidor)
2. Atualizar a URL do fetch no HTML de `http://localhost:8000` para a URL do servidor
3. Configurar CORS se necessário

### Opção 1: Rodar no mesmo servidor (casapropriajp.com)

```bash
# Em produção, use:
gunicorn -w 4 -b 0.0.0.0:8000 matome_api:app
```

Depois atualize a URL no HTML para: `http://casapropriajp.com/api/gerar-pdf`

### Opção 2: Rodar em servidor separado

Se rodar em outro servidor, a URL seria: `http://seu-servidor.com/api/gerar-pdf`

---

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'reportlab'"

Instale as dependências:
```bash
pip install reportlab fastapi uvicorn pydantic
```

### Erro: "Connection refused" no frontend

Certifique-se de que a API está rodando:
```bash
python matome_api.py
```

A API precisa estar rodando em `http://localhost:8000` para testes locais.

### PDF está vazio

Verifique se os dados estão sendo enviados corretamente. Abra o console do navegador (F12) e veja a requisição POST.

---

## Arquivos

- **matome_api.py** — API FastAPI
- **matome_pdf_generator.py** — Gerador de PDF com reportlab
- **matome-elementor.html** — Frontend atualizado com chamada à API
