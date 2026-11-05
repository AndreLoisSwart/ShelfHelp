# Future enhancements

Difficulty is rated 1 (trivial) to 5 (major project), as assessed on 2026-11-04 and 2026-11-05.

## V2 (decided)

### Handwritten notes

Pen input on a tablet for notes, with handwriting-to-text recognition so handwritten notes become searchable and editable.

Three levels, cheapest first:

| Level | What | Difficulty |
|---|---|---|
| A. The tablet's own handwriting keyboard | iPad Scribble, Samsung S Pen handwriting-to-text and Gboard's handwriting mode turn pen writing into text in any text field, including the note editor. No app changes | 1 |
| B. Ink notes | Draw in the app and keep the drawing | 3 |
| C. Ink plus recognition | Drawings that also become searchable text | 4 (cloud), 5 (fully local) |

**B, ink notes:**
- Capture strokes with Pointer Events. They report pressure and `pointerType`, so a resting palm (touch) can be ignored while the pen is down. `perfect-freehand` gives smooth, pressure-sensitive lines.
- Store strokes as data (points with x, y, pressure and time), not as a picture. Strokes stay sharp at any size, stay editable, and stroke-based recognition can read them later.
- Notes must stay plain markdown, so each drawing is an attachment (strokes plus a rendered image) and the note embeds the image with a normal markdown image tag.

**C, recognition:**
- *Stroke-based ("online")* recognition is the most accurate. Engines: MyScript iink (commercial), Google ML Kit Digital Ink (Android apps only). Chrome's Handwriting Recognition API exists but is only really available on ChromeOS.
- *Image-based* recognition: Tesseract is poor on handwriting. Handwriting models such as TrOCR could run on the N100 but slowly, and need line segmentation first. A cloud vision model (e.g. Claude) is the most accurate and least work, but costs per page and sends notes off the network.

**Status:** the user is trying level A first (2026-11-04). Build B only if keeping the ink itself (sketches, diagrams) matters; decide C after that.

**Open question:** which tablet and pen. It decides how good level A is.

## Ideas (not decided)

Candidates raised during design. None are committed. Each needs discussion before it is moved into a version.

### MCP server (difficulty 2–3 for phase 1, 4 for phase 2)

An MCP layer so Claude can do roughly what the app can: search, read and edit projects, items and notes, link items, sort the inbox, read the shopping list and dashboard, add links. The goal includes using it from the Claude mobile app in the workshop, where there is no computer.

**Constraint: no API billing.** It must work through the Claude subscription (Claude Code, Claude Desktop, the Claude mobile app). That rules out building an assistant into Shelf-help or using Home Assistant's Anthropic voice integration, since both run on a pay-per-use API key.

**Design:**
- An MCP endpoint inside the add-on (official Python MCP SDK, streamable HTTP at `/mcp`).
- Its tools call the existing service layer, so every rule (last touched, inbox flag, readiness, owner check) applies and nothing is duplicated.
- Hand-written tools (about 15) rather than tools generated from the OpenAPI spec: clearly named, task-shaped tools work much better for an assistant.
- Deletes left out at first, or marked destructive so the client asks before each one. Attachment upload left for later.
- **Login is its own layer in front of `/mcp`, separate from the tools.** The tools never know how a request was authenticated, so phase 2 adds a second kind of login without touching them.

**Which Claude clients can reach what:**

| Client | How it connects | Works on LAN/VPN only? |
|---|---|---|
| Claude Code | Connects to the MCP URL directly from the machine (`--transport http` with an `Authorization` header) | Yes |
| Claude Desktop | A local MCP server in its config file runs on the machine; a small bridge (e.g. `mcp-remote`) forwards to `/mcp` with the token | Yes |
| Claude mobile app, claude.ai | Custom connectors are called **from Anthropic's cloud**, not from the phone | **No.** The server must be reachable from the internet, over HTTPS, with OAuth |

The existing WireGuard VPN can't carry the mobile app's traffic: only your own devices join it, and Anthropic's servers can't. Mobile needs a separate public entry point for `/mcp` only, while WireGuard carries on as it is.

**Security ranking (effort aside):**

| Option | Who can reach it | Login |
|---|---|---|
| Token, LAN/VPN only | Your network and VPN | Long random secret |
| Public, OAuth | Anyone on the internet | Strong (short-lived tokens, PKCE) |
| Public, OAuth plus allowlist of Anthropic's published connector IP addresses | Only Anthropic's servers | Strong |

Not being on the internet is the most secure. OAuth is the right login *if* public, but it doesn't make public as safe as private: bots can find and probe a public endpoint, so a bug in login, the MCP library or the app matters more.

#### Phase 1: Claude Code and Desktop on LAN/VPN (decided order, not yet scheduled)

1. **Token auth on the direct port.**
   - Requests arriving through Ingress come from the Supervisor's gateway address (`172.30.32.2`) and are already authenticated by HA. Anything else must carry a bearer token, and may only reach `/mcp`. Everything else on the direct port gets 401.
   - This also closes today's gap where enabling port 8099 exposes the whole app without auth.
   - The token is long and random, generated on first start and kept in `/data`. It is shown and regenerated on the Settings page, which itself is only reachable through Ingress.
   - On the LAN the token travels as plain HTTP; over the VPN the tunnel encrypts it. Acceptable for a trusted network.
2. **The MCP server** with its tools.
3. **Connect Claude Code** directly, and **Claude Desktop** through the local bridge.

Use phase 1 for a while before deciding on phase 2. If it's mostly used at the desk, phase 2 can wait.

#### Phase 2: the Claude mobile app (after phase 1 works)

1. **OAuth on `/mcp`**, next to the token: an OAuth 2.1 flow with PKCE, as the MCP authorization spec and Claude's custom connectors expect. The tools stay unchanged.
2. **A public entry point for `/mcp` only.** Options:
   - **Cloudflare Tunnel (preferred):** the community "Cloudflared" HA add-on connects outward, so no router port is opened, and Cloudflare provides HTTPS. Needs a domain on Cloudflare (a cheap one works).
   - **Tailscale Funnel:** similar, with a free `*.ts.net` address and no domain needed.
   - **Router port forward plus a reverse proxy with a certificate:** puts the router directly on the internet. Least preferred.
3. **Lock it down in layers:** only `/mcp` routed; only Anthropic's published connector IP addresses allowed (check the current list); OAuth required.
4. **Add it in the Claude app** as a custom connector.

Phase 2 gives up the "nothing exposed to the internet" principle in `project-overview.md` for this one endpoint, so it needs an explicit decision, and that doc updated, when it happens.

### Barcode scanning and product lookup (difficulty 2 to scan, lookup coverage uncertain)

Scan a product's barcode with a phone or tablet camera to fill in the item name.

**Scanning:**
- A live camera preview needs `getUserMedia`, which browsers only allow on HTTPS pages (or localhost). HA is reached over plain `http://`, in the browser and the companion app, so **live scanning is blocked today**.
- The fallback works everywhere: an "upload photo" button that opens the camera (`<input type="file" accept="image/*" capture="environment">`), then the app decodes the barcode from the photo. Chrome on Android has a built-in `BarcodeDetector`; elsewhere a ZXing build (e.g. the `barcode-detector` polyfill) does it.
- Live scanning becomes possible if HA is later served over HTTPS.

**Lookup databases:**
- **Open Food Facts:** free, open (ODbL), international and crowd-sourced; sister databases Open Products Facts and Open Beauty Facts cover household and cosmetics. South African products (GS1 prefixes 600–601) are listed but coverage is much thinner than for Europe, especially for local and store brands. Missing products can be added through its app, which helps everyone.
- **UPCitemdb:** free tier of about 100 lookups a day, broader retail coverage, US-leaning.
- **Barcode Lookup, Go-UPC, EAN-Search:** paid, more complete.
- **Before building:** scan about 10 products from the cupboard and workshop against Open Food Facts to measure the real hit rate.

**Flow (agreed 2026-11-04):**
1. Scan.
2. If the barcode is found, the name is pre-filled; if not, type it once.
3. Either way, store the barcode on the item (a new nullable, unique `barcode` column).
4. Scanning a known barcode again finds the existing item and offers one tap to set Have or Need to get. Useful for restocking even when no database knows the product.

Recognising products without a barcode (from a photo) would need a cloud vision model, and is a separate, larger idea.

### Smaller ideas

- **Home Assistant sensors:** expose values such as "items low" or "active projects" to HA.
- **E-ink frame screen:** show the current project's next step on the e-ink picture frame.
- **Grocery shopping:** make the Home shopping list practical for groceries (e.g. recurring items).
- **Custom shopping lists:** in addition to the generated ones.
- **Item categories:** a category tree, if tags turn out not to be enough.
- **Photos:** progress photos on projects, photos of items.
- **Checkbox roll-up:** show open note checkboxes across projects as a task view.
- **Activity log:** a history per project.
- **Export:** markdown or JSON export of all data.
