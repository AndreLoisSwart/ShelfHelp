# Future enhancements

Difficulty is rated 1 (trivial) to 5 (major project), as assessed on 2026-11-04.

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

### MCP server (difficulty 2–3, plus auth)

An MCP layer so AI assistants can do roughly what the app can: search, read and edit projects, items and notes, link items, sort the inbox, read the shopping list and dashboard, add links.

**Design:**
- An MCP endpoint inside the add-on (official Python MCP SDK, streamable HTTP at `/mcp`).
- Its tools call the existing service layer, so every rule (last touched, inbox flag, readiness, owner check) applies and nothing is duplicated.
- Hand-written tools (about 15) rather than tools generated from the OpenAPI spec: clearly named, task-shaped tools work much better for an assistant.
- Deletes left out at first, or marked destructive so the client asks before each one. Attachment upload left for later.

**Auth comes first, and can be built before MCP.** Today the app is protected only by HA Ingress, and the direct port 8099 is disabled because it has no auth at all. MCP clients can't log in through Ingress.

Options, in order of effort:

1. **Token on the direct port (recommended first step).**
   - Requests arriving through Ingress come from the Supervisor's gateway address (`172.30.32.2`) and are already authenticated by HA. Anything else must carry a bearer token, and may only reach `/mcp`. Everything else on the direct port gets 401.
   - This also closes today's gap where enabling port 8099 exposes the whole app without auth.
   - The token is long and random, generated on first start and kept in `/data`. It is shown and regenerated on the Settings page, which itself is only reachable through Ingress.
   - Traffic on the LAN is plain HTTP, so the token is visible to anything sniffing the LAN. Over the VPN it is encrypted by the tunnel. Acceptable for a trusted network; TLS on the direct port is a later option.
2. **A separate MCP-only port.** Same token, but the app UI never listens outside Ingress. Slightly cleaner, one more port to manage.
3. **Public exposure with OAuth (only needed for the Claude mobile app and claude.ai).** See below.

**Which Claude clients can reach it:**

| Client | How it connects | Works on LAN/VPN only? |
|---|---|---|
| Claude Code | Connects to the MCP URL directly from the machine (`--transport http` with an `Authorization` header) | Yes |
| Claude Desktop | A local MCP server in its config file runs on the machine; a small bridge (e.g. `mcp-remote`) forwards to `/mcp` with the token | Yes |
| Claude mobile app, claude.ai | Custom connectors are called **from Anthropic's cloud**, not from the phone | **No.** Being on the VPN doesn't help: the server must be reachable from the internet, over HTTPS, normally with OAuth |

Mobile would therefore mean exposing `/mcp` publicly (Cloudflare Tunnel, Nabu Casa or similar), with HTTPS and an OAuth flow, and only `/mcp` reachable. That conflicts with the current "nothing exposed to the internet" principle, so it is a separate decision (difficulty 4).

**Recommendation:** build option 1, then MCP for Claude Code and Desktop. Decide on public exposure for mobile afterwards.

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
