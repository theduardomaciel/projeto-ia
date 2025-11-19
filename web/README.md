# Resume Analyzer Web UI

Modern SvelteKit + TailwindCSS 4 front-end that drives the resume analysis workflow defined in `src/`.

## Prerequisites
- Node.js 20+
- pnpm (project is configured with `packageManager: pnpm@9.11.0`)

## Setup & Commands
```bash
cd web
pnpm install
pnpm run dev    # local dev server at http://localhost:5173
pnpm run build  # production build (outputs to build/)
pnpm run preview
pnpm run check  # type-check + Svelte diagnostics
```

Set the backend base URL with a public env var recognized by SvelteKit:
```
PUBLIC_API_BASE_URL=https://localhost:8000
```
You can define it in a `.env` file inside `web/` or via your shell before running the dev server.

## Minimal Backend Contract Suggestion
- Endpoint: `POST /api/analyze`
- Content-Type: `multipart/form-data`
- Fields:
  - `job`: optional string identifier/path to the vacancy definition.
  - `resumes`: one or more files (`.pdf` or `.docx`).
- Response: JSON array of objects in the form:
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
- Error handling: reply with HTTP 4xx/5xx and a JSON body `{ "detail": "message" }` so the UI surfaces the text.

This interface expects the backend already orchestrates parsing, scoring, and (optionally) explainability modules defined under `src/`.
