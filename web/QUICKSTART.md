# Quick Start Guide - Web Interface

## Development Mode (with backend integration)

### 1. Start Frontend
```bash
cd web
pnpm install
pnpm dev
```
→ Opens at http://localhost:5173

### 2. Backend Options

**Option A - Use dev proxy (recommended)**
- Ensure backend runs at `http://localhost:8000`
- Frontend automatically proxies `/api/*` requests
- No CORS issues

**Option B - Different backend port**
```bash
BACKEND_URL=http://localhost:8001 pnpm dev
```

**Option C - Direct connection (no proxy)**
Create `web/.env`:
```env
PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 3. Test the Interface

1. **Check Status**
   - Header should show "Backend online" or "Backend não respondeu"

2. **Upload Resumes**
   - Drag & drop or select PDF/DOCX files
   - Optionally paste job description or upload job.txt

3. **Analyze**
   - Click "Enviar agora"
   - Results appear with ranking, skills, and explanations

## Backend Requirements

Implement these endpoints in your Python backend:

### Health Check (optional but recommended)
```
GET /api/health
→ 200 OK
```

### Analysis (required)
```
POST /api/analyze
Content-Type: multipart/form-data

Fields:
  - resumes: File[] (required)
  - job_text: string (optional)
  - job_file: File (optional)

Response:
[
  {
    "candidate_name": "João Silva",
    "hard_skills": ["python", "django"],
    "soft_skills": ["comunicação", "liderança"],
    "match_score": 85,
    "explanation": "Candidato com sólida experiência...",
    "ranking_position": 1
  }
]
```

## Troubleshooting

**"Backend não respondeu"**
- Check if backend is running
- Verify port (default: 8000)
- Check `BACKEND_URL` env var

**CORS errors**
- Use dev proxy mode (default)
- Or enable CORS in your backend

**File upload fails**
- Check file size limits in backend
- Verify multipart/form-data is supported
- Check backend logs for errors

**Results not displaying**
- Check browser console for errors
- Verify response matches expected JSON schema
- Ensure `ranking_position` is present or defaults to index

## Files Reference

- API client: `src/lib/api.ts`
- Main page: `src/routes/+page.svelte`
- Components: `src/lib/components/*.svelte`
- Config: `vite.config.ts`, `.env.example`
- Docs: `README.md`, `INTEGRATION.md`
