# CLAUDE.md — Shelf-help

Shelf-help is a personal project, item and notes manager. Single user, self-hosted as a Home Assistant add-on, reached locally or over VPN.

## Read before working

| File | What it covers |
|---|---|
| `docs/project-overview.md` | Purpose, principles, tech stack, hosting, repo structure, conventions |
| `docs/data-model.md` | Tables, fields, enums and the rules around them |
| `docs/pages.md` | Navigation, pages, overlays, reusable components, visual style |
| `docs/mvp.md` | What is in V1, build order, what is out of scope |
| `docs/future-enhancements.md` | Planned V2 work and unconfirmed ideas |

## Ground rules

- **Stay inside `docs/mvp.md`.** Don't build features from `future-enhancements.md` unless asked. If a change alters a decision, update the relevant doc in the same change.
- **Organise by feature, not by layer.** Backend: `backend/app/modules/<feature>/` (models, schemas, router, service). Frontend: `frontend/src/features/<feature>/`. Shared UI goes in `frontend/src/components/`; reusable components bound to one feature's data stay in that feature's folder.
- **Every schema change gets an Alembic migration.** Never edit the database by hand.
- **Regenerate the TypeScript API client after any API change.** Never hand-write API types on the frontend.
- **Business rules live in the service layer:** `last_touched_at` updates, inbox flag, the attachment owner check. Keep routers thin.
- **Readiness and the shopping list are computed.** Never store them.
- **Notes are stored as raw markdown.** The editor must round-trip to markdown cleanly.
- **The app runs behind HA Ingress under a changing path prefix.** Use relative asset paths (Vite `base: './'`) and read the router base path at runtime. Never hard-code absolute URLs.
- **All persistent data goes in `/data`:** the SQLite database and `/data/attachments/`. This keeps it in HA backups.
- **Keep the UI clean:** neutral theme, one accent colour. Status colours are the only other colour.

## Commands

Python is managed with `uv`, the frontend with `npm`. Local image builds use Podman (rootless); HAOS builds with its own Docker.

| Task | Command |
|---|---|
| Install backend deps | `cd backend && uv sync` |
| Install frontend deps | `cd frontend && npm install` |
| Backend dev server (port 8099, hot reload) | `cd backend && uv run uvicorn app.main:create_app --factory --reload --port 8099` |
| Frontend dev server (proxies `/api` to 8099) | `cd frontend && npm run dev` |
| Backend tests | `cd backend && uv run pytest` |
| Lint and format check (backend) | `cd backend && uv run ruff check . && uv run ruff format --check .` |
| Lint and format check (frontend) | `cd frontend && npm run lint` (fix formatting with `npm run format`) |
| Apply migrations to the dev database (`.data/`) | `cd backend && uv run alembic upgrade head` |
| Create a migration after changing models | `cd backend && uv run alembic revision --autogenerate -m "<what changed>"`, then review the generated file |
| Regenerate the API client after any API change | `cd frontend && npm run gen:api` |
| Build frontend (served by the backend from `frontend/dist`) | `cd frontend && npm run build` |
| Test behind a fake Ingress prefix (needs a built frontend and the backend on 8099) | `cd backend && uv run python scripts/ingress_proxy.py`, then open `http://localhost:8100/api/hassio_ingress/dev-token/` |
| Build the add-on image | `podman build -t shelf-help .` |
| Run the add-on image (open via `127.0.0.1`, not `localhost`: rootless Podman resets IPv6 connections) | `podman run --rm -p 8099:8099 -v ./.data:/data shelf-help` |

Notes:
- Data lives in `SHELF_DATA_DIR`: `.data/` at the repo root in dev, `/data` in the add-on.
- The add-on runs `alembic upgrade head` on every start (`addon/run.sh`).
- `tests/test_db.py` fails if models change without a matching migration.
- `npm run gen:api` exports the spec to `frontend/openapi.json` and regenerates `frontend/src/api/generated/`. Both are committed; never edit them by hand.
- Add shadcn components with `cd frontend && npx shadcn@latest add <name>`.

**Deploying:** the repo root is the add-on folder (`config.yaml` and `Dockerfile` live there). Clone it into `/addons` on HAOS, then install it from Settings → Add-ons → Add-on store → Local add-ons. To update, pull, bump `version` in `config.yaml`, and rebuild from the add-on page.
