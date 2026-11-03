# Shelf-help — project overview

## Purpose

Shelf-help is one place to manage personal projects, both active ones and "someday" ideas, along with the notes and items they need.

The underlying problem is that paper and loose lists get misplaced or forgotten. The app only works if it is quick to capture into and somewhere worth visiting regularly, so features are judged against that.

## Principles

1. **Capture must be fast.** Adding something takes a type and a name. Details get added later, from the inbox.
2. **Items exist on their own.** An item is created standalone and then *linked* to projects. Projects never own items.
3. **Low maintenance.** Quantities are not tracked. Status (Have / Low / Out / Need to get) is enough. Derived views (readiness, shopping list) are computed, so they never need upkeep.
4. **Show what to do next.** Every project has a next step and a last-touched date, so stalled projects are visible.
5. **Clean UI.** Neutral, uncluttered and usable on mobile. Colour is reserved for status.
6. **Built to grow.** Feature-module structure, so new features are new folders.

## Core concepts

- **Project:** anything from an idea to an ongoing build. Has a status, next step, notes, linked items, links and attachments.
- **Item:** a tool, component, consumable or household good. Can have a parent item (e.g. table saw → blade), a location, links and attachments.
- **Location:** a tree. Top-level locations (Home, Workshop) act as zones for filtering and shopping lists.
- **Note:** markdown (headings, checkboxes, etc.). Optionally belongs to a project.
- **Inbox:** anything quick-added that still needs sorting.
- **Readiness:** how many of a project's required items are on hand.
- **Shopping list:** every item with status Low, Out or Need to get, grouped by top-level location.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (with separate Pydantic schemas), Alembic, Pydantic |
| Database | SQLite (single file in `/data`) |
| Frontend | React, TypeScript, Vite |
| UI | shadcn/ui (Radix + Tailwind) |
| Data fetching | TanStack Query, with a TS client generated from FastAPI's OpenAPI spec (`orval`, which also generates the TanStack Query hooks) |
| Drag and drop | dnd-kit (project board) |
| Markdown editor | WYSIWYG editor that stores plain markdown (Milkdown or TipTap + markdown). Final choice open |

## Hosting

- Packaged as a **custom Home Assistant add-on**: one container in which FastAPI serves both the API and the built frontend.
- Opened through **HA Ingress**, as a sidebar panel that also works in the HA companion app and is protected by HA authentication.
- Optionally also exposed on a **direct LAN port** (8099) for desktop or browser use. It is **disabled by default** because it bypasses HA authentication, and is enabled from the add-on's Network settings in HA.
- **Ingress base path:** HA strips its prefix and sends it in `X-Ingress-Path`. When serving `index.html`, the backend injects it as a `<base>` tag and as `window.__BASE_PATH__`, which the frontend uses for the router basename and API URLs.
- **Remote access is through the existing VPN tunnel.** Nothing is exposed to the internet.
- **Data lives in `/data`** (database plus `/data/attachments/`), so it is included in HA backups. The add-on uses **cold backups**: HA stops it for a few seconds while backing up, so the SQLite file is never copied mid-write.
- **Migrations run automatically** every time the add-on starts.
- **Development happens on the desktop** (CachyOS) with hot reload. HAOS is for deployment only.
- **Code lives in its own GitHub repo** (`ShelfHelp`), separate from the Home Assistant automations repo. It is deployed by cloning into `/addons` on HAOS and installing it as a local add-on.

## Repo structure (target)

```
/
├─ CLAUDE.md
├─ config.yaml              # HA add-on config (at the root: HA uses this folder as the build context)
├─ Dockerfile               # HA add-on image: builds the frontend, then the Python app
├─ docs/
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # app factory, mounts routers + static frontend
│  │  ├─ core/              # config, db session, frontend serving, shared deps
│  │  └─ modules/
│  │     ├─ projects/
│  │     ├─ items/
│  │     ├─ locations/
│  │     ├─ notes/
│  │     ├─ tags/
│  │     ├─ links/
│  │     ├─ attachments/
│  │     ├─ inbox/
│  │     ├─ search/
│  │     └─ shopping/       # computed shopping list, no tables
│  ├─ migrations/           # Alembic
│  ├─ scripts/              # dev tools, e.g. the Ingress stand-in proxy
│  └─ tests/
├─ frontend/
│  └─ src/
│     ├─ api/               # generated client
│     ├─ components/        # shared reusable UI
│     ├─ lib/               # shared non-UI code, e.g. base path
│     └─ features/          # mirrors backend modules, plus dashboard, shopping and settings
└─ addon/                   # files copied into the add-on image, e.g. run script
```

## Conventions

- **Each backend module** contains `models.py`, `schemas.py`, `router.py` and `service.py`. Routers stay thin and rules live in services.
- **Migrations are required** for any schema change.
- **Regenerate the frontend API client** after any API change.
- **Use relative paths everywhere** because of Ingress.
- **Timestamps are UTC** in the database and converted to local time in the UI.
