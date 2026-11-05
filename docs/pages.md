# Pages and components

## Navigation

**Desktop**
- **Sidebar:** Home, Projects, Items, Notes, Shopping. Settings sits at the bottom.
- **Top bar:** search, inbox icon (with count) and a quick-add button.

**Mobile**
- **Bottom bar:** Home, Projects, **+** (quick-add, centre), Items, Shopping.
- **Top bar:** search and inbox icon. Notes and Settings are reached from a menu, or from projects and search.

**Inside the HA app**
- The app runs as an Ingress panel and must work inside the HA companion app's frame.
- It also works as a standalone browser tab or home-screen shortcut over the VPN.

## Pages

| Route | Page | Contents |
|---|---|---|
| `/` | Home | Dashboard, see below |
| `/projects` | Projects | Board (default) and list toggle; the choice is remembered per device. The board has a column per status, and dragging a card changes its status. Done and abandoned are hidden unless "Show finished" is on. Filter by tag; the list can also filter by status. Most recently touched first. Cards show status, readiness, next step and last touched |
| `/projects/:id` | Project details | Header with name, status, next step (editable) and readiness bar. Tabs: Overview (tags, description), Notes, Items (linked items with status, "link item"), Files & links. The open tab is kept in the URL. Until the markdown editor arrives (step 6) the description is a plain text box that stores markdown |
| `/items` | Items | List with location tree filter, plus status and tag filters. Child items appear indented under their parent |
| `/items/:id` | Item details | Status, location, parent and children, "Used in" (linked projects, opening their Items tab), links, attachments, description. "Used in" also links from this side: a picker of open projects (or create one), plus a Required / Nice to have switch and unlink on each row |
| `/notes` | Notes | All notes, most recently updated first, with a text excerpt. Filter by project or "No project" |
| `/notes/:id` | Note editor | Title, project assignment, markdown editor, links and attachments. Saves automatically shortly after typing stops and when leaving the page, with a Saving…/Saved indicator. Deleting goes to the project's Notes tab, or to Notes |
| `/shopping` | Shopping | One tab per top-level location, plus "Unassigned". Opens on the first zone with something to get. Rows show where in the zone the item lives and which projects it's for. Each row has a one-tap "Got it" (sets status to `have`) with an 8-second Undo. Tapping the row opens Item details |
| `/inbox` | Inbox | Records with `in_inbox`, grouped into items, projects and notes, newest first. Inline fields to sort each one (items: status, location, tags; projects: status, tags; notes: project) and a "Done" button that clears the flag, with Undo. Detail pages of inbox records show an "In the inbox" notice with its own Done button |
| `/settings` | Settings | Location tree editor, tag management, and when a project counts as stale (1 to 12 weeks). Later: export, backups |

There is deliberately **no shopping-list item detail page**. Shopping rows are items, so they open Item details.

The **project Notes tab** reuses the Notes list component, filtered to that project, and opens the same editor.

## Dashboard (Home)

Sections in priority order:

1. **Active projects with their next step.** Every `active` project, most recently touched first. The next step is editable inline on the card (which touches the project); the name opens it. The touched time turns orange when the project is stale. This is the most-used section.
2. **Running low.** A compact list (name, status badge, location) of items that are out, then low, capped at 6, with "and N more on the shopping list". Need-to-get items are left to the shopping list. Links to Shopping.
3. **Stale projects**, titled "Gone quiet". Smaller, a nudge rather than a guilt list: active or paused projects past the threshold, oldest first, e.g. "Table saw restoration — 6 weeks". Paused ones show their badge.

The page comes from one computed endpoint, `GET /api/dashboard`.

No inbox section, because the inbox icon already shows the count. On mobile the sections stack in this order. On desktop, active projects take the full width with the other two side by side below.

## Overlays

- **Quick-add:** a dialog on desktop and a bottom sheet on mobile, opened from the Add button (desktop), the bottom bar's **+** (mobile) or the search palette. Choose the type (Item / Note / Project, the last one used is remembered per device), enter a name, and for an item pick Have or Need to get. Enter saves to the inbox, closes, and shows a toast with an Open button; it never navigates away by itself.
- **Search:** a command palette (Ctrl+K or Cmd+K, or the search icon). Results are grouped into projects, items and notes, up to 5 each, with matched words highlighted and a status badge for projects and items. Selecting one navigates to it. With nothing typed it lists the pages and Quick add.

## Reusable components

Generic components live in `frontend/src/components/`. Components bound to one feature's data (`ItemRow`, `LocationTreeSelect`, `TagEditor`) live in that feature's folder.

| Component | Used for |
|---|---|
| `StatusBadge` | Project and item status, colour-coded |
| `ReadinessBar` | Project cards and header. Hidden when a project has no required items |
| `TagChips` | Projects and items |
| `ProjectCard` | Projects list and board, dashboard |
| `ItemRow` | Items list, project Items tab, shopping, dashboard |
| `EntityPicker` | Search existing records with "create new" (e.g. linking items to a project) |
| `LocationTreeSelect` | Item location, items filter |
| `MarkdownEditor` | Note editor, project description. Toolbar (headings, bold, italic, strikethrough, link, lists, checklist, quote, code block) plus markdown shortcuts as you type. Loaded on demand, since it is most of the bundle |
| `LinkList` | Links on projects, items and notes. Add a URL and optional title; a link without a title shows its domain |
| `AttachmentList` | Attachments on projects, items and notes. Upload several at once; PDFs and images open in a new tab, other files download |
| `PageHeader` | All pages |
| `DetailLayout` | Header plus tabs for detail pages |
| `FilterBar` | List pages |
| `EmptyState` | Any empty list |
| `ConfirmDialog` | Deletes and other destructive actions |
| `EditableText` | Names and descriptions edited in place (saves on blur or Enter) |
| `InlineAddForm` | Adding locations and tags in Settings |
| `TagEditor` | Assigning tags to projects and items, creating new ones on the fly |
| `QuickAddSheet` | Quick-add overlay (`features/inbox`, opened anywhere with `useQuickAdd()`) |
| `SearchPalette` | Search overlay (`features/search`) |

## Visual style

- **Base:** shadcn neutral theme (Nova preset, Geist font, lucide icons) with one accent colour: **muted blue**.
- **Light and dark:** follows the device's colour scheme. There is no manual toggle.
- **Colour:** status colours are the only other colour, so "Out", "Need" and stale projects stand out. Tokens are defined in `frontend/src/index.css` (`bg-status-green`, `text-status-red`, etc.):

  | Colour | Used for |
  |---|---|
  | Green | Item `have`, project `active` |
  | Amber | Item `low`, project `paused` |
  | Red | Item `out` |
  | Violet | Item `need`, project `planned` |
  | Orange | Stale projects |
  | Neutral (no colour) | Project `someday`, `done`, `abandoned` |

- **Layout:** generous spacing, few borders. Must be usable at phone width without horizontal scrolling.
