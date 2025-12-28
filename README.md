# Frontend Technical Assessment — Project README

This repository contains a small React + React Flow frontend and a lightweight FastAPI backend used for a pipeline/node-based assessment. This README explains how to run the project, test the POST parsing endpoint, and describes the code architecture so you can find and modify pieces quickly.

**Quick Links**
- Backend parse endpoint: [backend/main.py](backend/main.py)
- Frontend entry: [frontend/src/index.js](frontend/src/index.js)
- Node components: [frontend/src/nodes](frontend/src/nodes)
- Global store: [frontend/src/store.js](frontend/src/store.js)
- Submit UI: [frontend/src/submit.js](frontend/src/submit.js)

## Quick start

Prerequisites:
- Node.js (>=14) and `npm` for the frontend
- Python 3.9+ and `pip` for the backend

1. Install backend dependencies and run the API server

```powershell
cd backend
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn
python -m uvicorn main:app --reload
# server will run at http://127.0.0.1:8000
```

2. Install and run the frontend

```bash
cd frontend
npm install
npm start
# opens http://localhost:3000 by default
```

3. Submit pipeline from the UI
- Open the app in the browser and click the `Submit Pipeline` button (in the toolbar area). The app will POST the current `nodes` and `edges` to the backend and show a centered animated success or error modal with the results.


The backend responds with JSON:

```json
{ "num_nodes": 2, "num_edges": 1, "is_dag": true }
```

## What the parse endpoint does
- File: [backend/main.py](backend/main.py)
- POST `/pipelines/parse` expects a JSON body with `nodes` (array of node objects containing `id`) and `edges` (array of objects with `source` and `target`).
- The endpoint computes:
  - `num_nodes`: number of unique valid node ids provided
  - `num_edges`: number of edges that reference known nodes
  - `is_dag`: whether the directed graph defined by edges is acyclic (Kahn's algorithm)
- For convenience, GET `/pipelines/parse` returns a short usage message and the last POSTed `nodes`/`edges`.

## Frontend architecture

- Main application: [frontend/src/App.js](frontend/src/App.js)
- Node UI abstraction: `BaseNode` — [frontend/src/nodes/BaseNode.js](frontend/src/nodes/BaseNode.js)
  - `BaseNode` centralizes header, body, and handle rendering for input/output handles. It reads `node.data.variables` when `inputs` are not explicitly passed.
- Node implementations: [frontend/src/nodes](frontend/src/nodes)
  - Thin wrappers (e.g., `inputNode.js`, `llmNode.js`, `outputNode.js`, `textNode.js`) render content and pass `inputs`/`outputs` into `BaseNode`.
  - `textNode.js` detects templated variables like `{{var}}`, persists `variables` into `node.data`, and renders text editing UI.
- Global state/store: [frontend/src/store.js](frontend/src/store.js)
  - Uses Zustand to maintain `nodes`, `edges`, and handlers for React Flow: `onNodesChange`, `onEdgesChange`, and `onConnect`.
  - `onConnect` now uses the handle ids from the React Flow connection event directly to create deterministic edges.
- Drag/toolbar and registration: [frontend/src/ui.js](frontend/src/ui.js) and [frontend/src/toolbar.js](frontend/src/toolbar.js)

## UI / Theming
- Global theme variables and layout are in [frontend/src/index.css](frontend/src/index.css).
- Nodes styling is in [frontend/src/nodes/node.css](frontend/src/nodes/node.css) and adjusted to provide larger clickable handle areas and labels.

## Submit flow and success UI
- File: [frontend/src/submit.js](frontend/src/submit.js)
  - Clicking the submit button sends `{nodes, edges}` to the backend.
  - A centered animated modal displays the result (`num_nodes`, `num_edges`, `is_dag`) on success or an error message on failure. Success auto-dismisses after a few seconds.

## Common development notes
- If React Flow prints warnings like "Couldn't create edge for target handle id...", it usually indicates a timing or id mismatch between a connection event and mounted handles. The app uses deterministic handle ids (prefixed by node id) and a short delay when creating edges to reduce races.
- To debug runtime state, inspect `useStore` in the browser console (the app exposes nodes/edges in React state) or add temporary logging in `frontend/src/store.js`.

## Troubleshooting
- 405 Method Not Allowed when visiting `/pipelines/parse` in a browser: this endpoint expects POST for parsing; a GET now returns a usage message. Use `POST` for parse behavior.
- PowerShell users: prefer `Invoke-RestMethod` or `curl.exe --%` when sending JSON bodies to avoid PowerShell string-parsing issues.

## Next steps you might want to implement
- Persist pipelines to disk or a small DB instead of in-memory `last_submission`.
- Improve edge-to-handle anchoring by explicitly mapping React Flow internal handle ids if you need pixel-perfect anchored edges.
- Add tests for the backend DAG detection logic (`backend/tests` + `pytest`).

---

If you'd like, I can also add a minimal `requirements.txt` for the backend and a short set of frontend unit tests. Tell me which you'd prefer next.
