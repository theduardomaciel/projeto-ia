# Resume Analyzer Web UI

Modern SvelteKit + TailwindCSS 4 front-end for the resume analysis pipeline defined in `src/`.

## Prerequisites
- Node.js 20+
- pnpm (configured as `packageManager: pnpm@9.11.0`)

## Setup & Commands
```bash
cd web
pnpm install
pnpm run dev    # local dev server at http://localhost:5173
pnpm run build  # production build (outputs to build/)
pnpm run preview
pnpm run check  # type-check + Svelte diagnostics
```

## Backend Integration

Two options during development:

1. **Dev proxy (recommended)**: Leave `PUBLIC_API_BASE_URL` unset. The app calls relative `/api/*` which Vite proxies to `http://localhost:8000` (or `BACKEND_URL` if set).
   - Override target: set `BACKEND_URL=http://localhost:8001` before `pnpm dev`.
2. **Direct calls**: Set `PUBLIC_API_BASE_URL=http://localhost:8000/api` to call the backend directly from the browser.

Copy `.env.example` to `.env` if you want to override defaults.

```env
# Use Vite dev proxy (default)
# PUBLIC_API_BASE_URL=/api
# Or call backend directly
# PUBLIC_API_BASE_URL=http://localhost:8000/api
# Optional: set proxy target
# BACKEND_URL=http://localhost:8000
```

The UI performs a lightweight health check on load and displays backend status in the header.

## API Contract

### Health Check (optional)
- **Endpoint**: `GET /api/health` or `GET /health`
- **Response**: 200 OK when the backend is ready

### Analysis
- **Endpoint**: `POST /api/analyze` (or `/analyze` if your base already includes `/api`)
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `resumes`: one or more files (`.pdf` or `.docx`)
  - Optional job specification (any of):
    - `job`: string identifier/path to the vacancy definition
    - `job_text`: raw text of the vacancy description
    - `job_file`: `.txt` file with the vacancy description
- **Response**: JSON array or `{ data: [...] }` with items:
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
- **Error**: HTTP 4xx/5xx with a textual body. The UI will display the message.

This interface assumes the backend orchestrates parsing, scoring and (optionally) explainability modules under `src/`.

For more details, see [INTEGRATION.md](./INTEGRATION.md).
