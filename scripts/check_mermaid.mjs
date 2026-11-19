// Verifies that every Mermaid diagram in the built site renders, in headless Chrome over the DevTools protocol.
//
//   node scripts/check_mermaid.mjs BASE_URL CHROME_DEBUG_PORT      e.g. http://127.0.0.1:8765 9333
//
// The expected number of diagrams per page comes from the Markdown source (```mermaid fences), so a page that has not
// loaded, or renders fewer diagrams than it declares, fails. The theme renders each diagram into a CLOSED shadow root on
// a new div.mermaid and leaves the original <pre class="mermaid"> in place when Mermaid throws a parse error;
// DOM.getDocument({pierce: true}) reaches the closed roots, so each SVG is checked for Mermaid's error role. Needs Node 22+
// (global WebSocket). Mermaid itself is loaded by the theme from unpkg.com, so this needs network access.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const [base, port] = process.argv.slice(2);
if (!base || !port) {
  console.error("usage: node scripts/check_mermaid.mjs BASE_URL CHROME_DEBUG_PORT");
  process.exit(2);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function markdown(dir) {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? markdown(path) : name.endsWith(".md") ? [path] : [];
  });
}
const pages = markdown("docs")
  .map((path) => [relative("docs", path), (readFileSync(path, "utf8").match(/^```mermaid\s*$/gm) ?? []).length])
  .filter(([, n]) => n > 0)
  .map(([rel, n]) => [rel === "index.md" ? "" : rel.endsWith("index.md") ? rel.slice(0, -8) : rel.slice(0, -3) + "/", n]);

const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0;
const pending = new Map();
ws.addEventListener("message", (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
});
const send = (method, params = {}) => new Promise((resolve) => { const n = ++id; pending.set(n, resolve); ws.send(JSON.stringify({ id: n, method, params })); });
await send("Page.enable");
await send("DOM.enable");

const probe = `(() => ({
  rendered: document.querySelectorAll('div.mermaid').length,
  unrendered: document.querySelectorAll('pre.mermaid').length,
  scheme: document.body ? document.body.getAttribute('data-md-color-scheme') : null,
}))()`;
function svgs(node, out = []) {
  for (const root of node.shadowRoots ?? []) {
    const stack = [...(root.children ?? [])];
    while (stack.length) {
      const n = stack.pop();
      if (n.nodeName === "svg") out.push(n);
      stack.push(...(n.children ?? []));
    }
  }
  for (const child of node.children ?? []) svgs(child, out);
  return out;
}
const attr = (n, name) => { const a = n.attributes ?? []; const i = a.indexOf(name); return i >= 0 ? a[i + 1] : null; };

let failures = 0;
let total = 0;
for (const [page, want] of pages) {
  await send("Page.navigate", { url: `${base}/${page}` });
  let r = {};
  for (let i = 0; i < 60; i += 1) {
    await sleep(500);
    r = (await send("Runtime.evaluate", { expression: probe, returnByValue: true })).result?.result?.value ?? {};
    if (r.rendered === want && r.unrendered === 0) break;
  }
  const doc = (await send("DOM.getDocument", { depth: -1, pierce: true })).result.root;
  const found = svgs(doc).filter((s) => (attr(s, "id") ?? "").startsWith("__mermaid_"));
  const errors = found.filter((s) => attr(s, "aria-roledescription") === "error").length;
  const ok = r.rendered === want && r.unrendered === 0 && found.length === want && errors === 0 && r.scheme === "slate";
  if (!ok) failures += 1;
  total += ok ? want : 0;
  console.log(`${ok ? "ok  " : "FAIL"} /${page} expected=${want} rendered=${r.rendered} svg=${found.length} errors=${errors} unrendered=${r.unrendered} scheme=${r.scheme}`);
}
const expected = pages.reduce((sum, [, n]) => sum + n, 0);
console.log(`${failures ? "FAILED" : "OK"}: ${total} of ${expected} Mermaid diagrams rendered on ${pages.length} pages; ${failures} page(s) failing.`);
ws.close();
process.exit(failures ? 1 : 0);
