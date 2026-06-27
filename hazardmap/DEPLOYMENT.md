# ハザードマップ API — Deployment Guide

## Live Endpoint (Production)

**URL:** `https://YOUR-PROJECT.railway.app`

Replace `YOUR-PROJECT` with your actual Railway project name.

---

## Health Check

```bash
curl https://YOUR-PROJECT.railway.app/
```

Expected response:
```json
{"status":"ok","service":"ハザードマップ API"}
```

---

## Generate Hazard Map PDF

### Request

```bash
curl -X POST https://YOUR-PROJECT.railway.app/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "cep": "5191424",
    "tipo": "1",
    "corretor": "João Silva"
  }'
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cep` | string | Yes | 7-digit Japanese CEP (e.g. "5191424") |
| `tipo` | string | No | Risk type: "1"=洪水, "2"=内水, "3"=高潮, "4"=津波, "5"=土砂災害 (default: "1") |
| `corretor` | string | No | Realtor name (optional) |

### Response (Success - 200)

```json
{
  "status": "success",
  "endereco": {
    "cep": "〒519-1424",
    "prefeitura": "三重県",
    "municipio": "鈴鹿市",
    "bairro": "中町"
  },
  "tipo": "洪水ハザードマップ",
  "downloads": {
    "mapa_pdf": "https://YOUR-PROJECT.railway.app/download/abc123.pdf",
    "comprovante": "https://YOUR-PROJECT.railway.app/download/comp_abc123.pdf"
  }
}
```

### Response (Errors)

**Invalid CEP (400):**
```json
{"detail":"CEP inválido. Use formato: 5191424 (7 dígitos)"}
```

**Invalid Type (400):**
```json
{"detail":"Tipo inválido. Use um de: 1, 2, 3, 4, 5"}
```

**Server Error (500):**
```json
{"detail":"Erro ao gerar PDF: ..."}
```

---

## Download PDFs

### Hazard Map

```bash
curl https://YOUR-PROJECT.railway.app/download/{filename}.pdf \
  -o hazardmap.pdf
```

### Legal Proof (Comprovante)

```bash
curl https://YOUR-PROJECT.railway.app/download/comp_{filename}.pdf \
  -o comprovante.pdf
```

---

## Supported Risk Types

| Tipo | Name | English |
|------|------|---------|
| 1 | 洪水ハザードマップ | Flood Hazard Map |
| 2 | 内水ハザードマップ | Internal Water Hazard Map |
| 3 | 高潮ハザードマップ | Storm Surge Hazard Map |
| 4 | 津波ハザードマップ | Tsunami Hazard Map |
| 5 | 土砂災害ハザードマップ | Landslide Hazard Map |

---

## Environment Variables

Set these in Railway dashboard under **Variables**:

```
BASE_URL=https://YOUR-PROJECT.railway.app
PORT=8000
```

---

## Local Development

### Setup

```bash
cd hazardmap
py -3.11 -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
playwright install chromium
```

### Run

```bash
uvicorn main:app --reload --port 8000
```

API available at: `http://localhost:8000`

### Test

```bash
curl -X POST http://localhost:8000/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{"cep":"5191424","tipo":"1","corretor":"Test"}'
```

---

## Docker Build & Test Locally

```bash
# Build image
docker build -t hazardmap:latest .

# Run container
docker run -p 8000:8000 \
  -e BASE_URL=http://localhost:8000 \
  hazardmap:latest

# Test
curl http://localhost:8000/
```

---

## Deploy to Railway

### Prerequisites

- Railway.app account (free)
- Railway CLI installed: `npm install -g @railway/cli`

### Steps

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize Railway project**
   ```bash
   cd Mirai/hazardmap
   railway init
   ```

3. **Deploy**
   ```bash
   railway up
   ```
   
   This builds Docker image and deploys. Takes ~3-5 minutes.
   Output includes the live URL.

4. **Set environment variable**
   ```bash
   railway variables set BASE_URL=https://YOUR-PROJECT.railway.app
   ```

5. **Verify deployment**
   ```bash
   curl https://YOUR-PROJECT.railway.app/
   ```

---

## Testing the API (MVP Validation)

### Test CEPs

Use these real Japanese CEPs to validate:

```bash
# Suzuka, Mie
curl -X POST https://YOUR-PROJECT.railway.app/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{"cep":"5191424","tipo":"1","corretor":"Test"}'

# Tokyo, Chiyoda (if available)
curl -X POST https://YOUR-PROJECT.railway.app/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{"cep":"1000001","tipo":"1","corretor":"Test"}'
```

### Expected Behavior

1. Request returns 200 with download links within 15-20 seconds
2. Both PDF files download successfully
3. Hazard map PDF opens in browser and shows map
4. Comprovante PDF opens and shows table with metadata

### Invalid Input Tests

```bash
# Invalid CEP
curl -X POST https://YOUR-PROJECT.railway.app/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{"cep":"123","tipo":"1"}'
# Expected: 400 error

# Invalid tipo
curl -X POST https://YOUR-PROJECT.railway.app/gerar-pdf \
  -H "Content-Type: application/json" \
  -d '{"cep":"5191424","tipo":"9"}'
# Expected: 400 error
```

---

## Architecture

```
[FastAPI Server]
    ↓
[geocode.py] → ZipCloud + GSI APIs
    ↓
[hazardmap.py] → Playwright + Chromium
    ↓
[comprovante.py] → ReportLab PDF
    ↓
[Downloads] → /pdfs directory
```

---

## Troubleshooting

### PDF generation takes too long (> 30s)

- Railway container may be underpowered
- Increase resources in Railway dashboard if needed
- Normal time: 15-20 seconds per request

### CEP not found error

- Verify CEP is valid 7 digits
- Some very rural areas may not be in ZipCloud database
- Try another CEP

### PDFs don't download

- Check if PDF files were created in `/pdfs` directory (via logs)
- Verify filename in URL matches actual file

### SSL/Certificate errors

- Use `--trusted-host` when installing locally
- Docker handles certificates automatically

---

## Next Steps (Future Phases)

- **Phase 2:** WordPress/Elementor integration (frontend HTML)
- **Phase 3:** Persistent storage (Railway Volumes or AWS S3)
- **Phase 4:** Analytics and logging
- **Phase 5:** Integration with VISION project

---

## Support

For issues or questions about this API, check:
- Railway dashboard logs: `railway logs`
- Local errors: Run with `--reload` flag for detailed output
- API spec: See `docs/superpowers/specs/2026-06-27-hazardmap-design.md`
