# Backend Integration Notes

This UI is ready to integrate with a Python backend that exposes a simple HTTP API. During dev, the app uses a Vite proxy to avoid CORS.

## Dev Modes
- Proxy (recommended): keep `PUBLIC_API_BASE_URL` unset. The UI calls relative `/api/*`, which is proxied to `http://localhost:8000`.
  - Override with `BACKEND_URL=...` before `pnpm dev`.
- Direct: set `PUBLIC_API_BASE_URL` (e.g., `http://localhost:8000/api`) to call the backend directly from the browser.

## Endpoints
- `GET /api/health` (optional): returns 200 when ready. The UI runs a health check on load.
- `POST /api/analyze` (or `/analyze` if your base includes `/api`): accepts `multipart/form-data` with the following fields:
  - `resumes`: one or more files (pdf/docx)
  - `job` (optional): string identifier/path for the vacancy; or
  - `job_text` (optional): vacancy description as text; or
  - `job_file` (optional): a `.txt` file with the vacancy description

Response: Array of candidate results or `{ data: [...] }`.

```json
{
  "candidate_name": "Maria Santos",
  "hard_skills": ["python", "rest api", "postgresql"],
  "soft_skills": ["comunicacao", "proatividade"],
  "match_score": 92,
  "explanation": "Pontuação alta em requisitos core e cinco anos trabalhando com APIs.",
  "ranking_position": 1
}
```

On error, return HTTP 4xx/5xx with a textual body. The UI will surface the message.

## Folder Cross-Refs
- Front code: `src/routes/+page.svelte`, `src/lib/api.ts`
- Env samples: `.env.example`
- Dev proxy: `vite.config.ts`
