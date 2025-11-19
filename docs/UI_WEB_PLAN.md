# UI Web Plan

## Goals
- Provide a modern, responsive UI for the resume-analysis pipeline using TailwindCSS and Svelte for component structure.
- Support multi-file upload (drag & drop + input) with progress and previews.
- Display ranked analysis results returned by the backend as JSON.

## Stack & Structure
- **Framework**: SvelteKit (Svelte 5.43.12) + TypeScript for routing and SSR friendliness.
- **Styling**: TailwindCSS 4.1.17 via `@tailwindcss/vite` plugin, using `@import "tailwindcss";` inside `src/app.css`.
- **Folder**: `web/` at repo root with SvelteKit routing (`src/routes/+layout.svelte`, `src/routes/+page.svelte`).

## Main Components
1. `UploadPanel.svelte`
   - Handles drag/drop, file picker, validations (PDF/DOCX), and progress indicators.
   - Emits selected files and triggers upload via a provided callback.
2. `ResultsTable.svelte`
   - Displays ranking list with sorting (score, name, position).
3. `CandidateCard.svelte`
   - Summaries per candidate: hard/soft skill tags, explanation, match score progress bar.
4. `EmptyState.svelte`
   - Guidance when no uploads yet.

## State & Flow
1. User adds files via drag/drop or button.
2. UI builds a `FormData` payload and calls `POST /api/analyze` (configurable base URL via `PUBLIC_API_BASE_URL`).
3. While awaiting response, progress bar animates; upon success the response array populates local store.
4. Results view renders candidate cards plus ranking table; sorting toggles update derived order.

## Backend Contract (default suggestion)
- Endpoint: `POST /api/analyze`
- Payload: multipart form with `job` (optional) and `resumes[]` files or JSON with file metadata if already uploaded.
- Response: JSON list of objects following the schema:
```json
{
  "candidate_name": "string",
  "hard_skills": ["python", "rest"],
  "soft_skills": ["leadership"],
  "match_score": 0,
  "explanation": "",
  "ranking_position": 1
}
```

## Error Handling & UX
- Validate file types client-side; show toast-like inline messages.
- Display API errors in a dismissible alert.
- Persist last results in memory (no storage) to keep scope focused.
