#!/usr/bin/env python3
"""Vault dashboard generator.

Scans every markdown note in the vault, parses its YAML frontmatter, pulls git
history, and renders a self-contained dashboard.html at the vault root.
Run it any time; it is idempotent. Called automatically by the Claude Code
PostToolUse hook whenever a file in the vault is written.
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(VAULT, "dashboard.html")
SECTIONS = ["course", "daily", "knowledge", "projects", "decisions", "references"]

TYPE_COLORS = {
    "daily": "#e9c46a", "note": "#2a9d8f", "project": "#e63946",
    "reference": "#457b9d", "index": "#8d99ae", "course": "#9d4edd", "week": "#9d4edd",
    "adr": "#f4a261",
}


def parse_frontmatter(text):
    meta = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip()
    return meta


def parse_list(value):
    """'[a, b]' or '["[[a]]", "[[b]]"]' -> ['a', 'b']"""
    if not value:
        return []
    items = re.findall(r'[\w][\w\- .]*', value.strip("[] "))
    return [i.strip() for i in items if i.strip() and i.strip() not in ("", '"')]


def excerpt(text):
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    for para in body.split("\n\n"):
        para = para.strip()
        if para and not para.startswith(("#", "|", "!", "-", ">", "```", "<!--")):
            plain = re.sub(r"\[\[([^\]]+)\]\]", r"\1", para)
            plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
            plain = re.sub(r"[*_`]", "", plain)
            return (plain[:220] + "…") if len(plain) > 220 else plain
    return ""


def collect_notes():
    notes = []
    for section in SECTIONS:
        d = os.path.join(VAULT, section)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(d, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            meta = parse_frontmatter(text)
            notes.append({
                "section": section,
                "file": f"{section}/{fn}",
                "slug": fn[:-3],
                "title": meta.get("title", fn[:-3]),
                "type": meta.get("type", "note"),
                "created": meta.get("created", ""),
                "status": meta.get("status", ""),
                "source": meta.get("source", ""),
                "tags": parse_list(meta.get("tags", "")),
                "related": re.findall(r"\[\[([^\]]+)\]\]", meta.get("related", "")),
                "excerpt": excerpt(text),
                "mtime": os.path.getmtime(path),
            })
    return notes


def git_log():
    try:
        out = subprocess.run(
            ["git", "log", "--pretty=format:%h|%ad|%s", "--date=format:%Y-%m-%d %H:%M", "-12"],
            cwd=VAULT, capture_output=True, text=True, timeout=10).stdout
        return [line.split("|", 2) for line in out.splitlines() if line.count("|") >= 2]
    except Exception:
        return []


PENDING_SKIP = {"dashboard.html", "review.html", ".DS_Store"}


def git_pending():
    """Uncommitted writes: [(state, path)] where state is 'modified' or 'new'."""
    try:
        out = subprocess.run(["git", "status", "--porcelain"],
                             cwd=VAULT, capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return []
    pending = []
    for line in out.splitlines():
        code, path = line[:2], line[3:].strip().strip('"')
        if os.path.basename(path) in PENDING_SKIP:
            continue
        if code.strip() == "??":
            full = os.path.join(VAULT, path)
            if os.path.isdir(full):
                for root, _, files in os.walk(full):
                    for f in sorted(files):
                        if f not in PENDING_SKIP:
                            pending.append(("new", os.path.relpath(os.path.join(root, f), VAULT)))
            else:
                pending.append(("new", path))
        else:
            pending.append(("modified", path))
    return pending


def render(notes, pending):
    now = datetime.now().strftime("%A, %B %-d %Y · %H:%M:%S")
    tags = {}
    for n in notes:
        for t in n["tags"]:
            tags[t] = tags.get(t, 0) + 1
    counts = {s: sum(1 for n in notes if n["section"] == s) for s in SECTIONS}
    commits = git_log()

    # discover standalone HTML pages (explainers, review, decks) to link from the header
    pages = []
    for root, _dirs, files in os.walk(VAULT):
        if "/.git" in root:
            continue
        for fn in sorted(files):
            if fn.endswith(".html") and fn != "dashboard.html":
                rel = os.path.relpath(os.path.join(root, fn), VAULT)
                label = fn[:-5].replace("-", " ").replace("_", " ").title()
                pages.append((rel, label))
    pages_html = ""
    if pages:
        links = "".join(f'<a class="page-link" href="{html.escape(p)}">📄 {html.escape(l)}</a>' for p, l in pages)
        pages_html = f'<div class="pages">{links}</div>'

    if pending:
        rows = "".join(
            f'<div class="pending-row"><span class="pstate {st}">{"✏️ modified" if st == "modified" else "🆕 new"}</span>'
            f'<code>{html.escape(p)}</code></div>'
            for st, p in pending)
        pending_html = f'''<section id="pending"><h2>⚖️ Pending review <span class="count">{len(pending)}</span></h2>
<div class="pending-box">
{rows}
<div class="pending-actions">
<a class="btn" href="review.html">Read the full diffs → review.html</a>
<span class="hint">approve in terminal: <code>git add -A && git commit</code> · reject: <code>git checkout -- &lt;file&gt;</code></span>
</div>
</div></section>'''
    else:
        pending_html = ('<section id="pending"><h2>⚖️ Pending review <span class="count">0</span></h2>'
                        '<div class="pending-box clean">Nothing awaiting approval — the vault is clean ✅</div></section>')

    def card(n):
        color = TYPE_COLORS.get(n["type"], "#2a9d8f")
        tag_html = "".join(f'<span class="tag" data-tag="{html.escape(t)}">#{html.escape(t)}</span>' for t in n["tags"])
        rel_html = "".join(f'<span class="rel">↔ {html.escape(r)}</span>' for r in n["related"])
        status = f'<span class="status">{html.escape(n["status"])}</span>' if n["status"] else ""
        return f'''<a class="card" href="{html.escape(n["file"])}" data-search="{html.escape((n["title"] + " " + " ".join(n["tags"]) + " " + n["excerpt"]).lower())}" data-tags="{html.escape(",".join(n["tags"]))}">
<div class="card-top" style="background:{color}"></div>
<div class="card-body">
<div class="card-head"><span class="type" style="color:{color}">{html.escape(n["type"])}</span>{status}<span class="date">{html.escape(n["created"])}</span></div>
<h3>{html.escape(n["title"])}</h3>
<p>{html.escape(n["excerpt"])}</p>
<div class="meta">{tag_html}{rel_html}</div>
</div></a>'''

    section_html = ""
    section_meta = [
        ("course", "🎓 Course"), ("projects", "🚀 Projects"), ("knowledge", "🧠 Knowledge"),
        ("decisions", "⚖️ Decisions"), ("references", "🔗 References"), ("daily", "📅 Daily notes"),
    ]
    for key, label in section_meta:
        items = [n for n in notes if n["section"] == key]
        items.sort(key=lambda n: (n["created"], n["mtime"]), reverse=True)
        if not items:
            continue
        cards = "\n".join(card(n) for n in items)
        section_html += f'<section><h2>{label} <span class="count">{len(items)}</span></h2><div class="grid">{cards}</div></section>\n'

    tag_html = "".join(
        f'<button class="tag big" data-tag="{html.escape(t)}">#{html.escape(t)} <b>{c}</b></button>'
        for t, c in sorted(tags.items(), key=lambda kv: -kv[1]))

    commit_html = "".join(
        f'<div class="commit"><code>{html.escape(h)}</code><span class="date">{html.escape(d)}</span><span>{html.escape(s)}</span></div>'
        for h, d, s in commits) or '<div class="commit"><span>no commits yet</span></div>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vault Dashboard</title>
<style>
:root {{ --bg:#0d1321; --surface:#1b2436; --text:#f1faee; --muted:#8d99ae; --accent:#e9c46a; --red:#e63946; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:radial-gradient(ellipse at 30% -20%, #101a33 0%, #060a14 55%, #03060d 100%); background-attachment:fixed; color:var(--text); font-family:'Helvetica Neue',Helvetica,Arial,sans-serif; padding:36px clamp(16px,4vw,60px) 80px; min-height:100vh; }}
#stars {{ position:fixed; inset:0; width:100%; height:100%; z-index:-1; pointer-events:none; }}
header h1 {{ font-size:clamp(28px,4vw,44px); letter-spacing:-1px; }}
header h1 span {{ background:linear-gradient(135deg,var(--red),var(--accent)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.updated {{ color:var(--muted); font-size:14px; margin-top:6px; }}
.updated b {{ color:var(--accent); font-weight:600; }}
.pages {{ margin-top:14px; display:flex; flex-wrap:wrap; gap:10px; }}
.page-link {{ display:inline-flex; align-items:center; gap:6px; background:rgba(157,78,221,.15); border:1px solid rgba(157,78,221,.5); color:#f1faee; text-decoration:none; border-radius:20px; padding:7px 15px; font-size:13.5px; transition:background .15s; }}
.page-link:hover {{ background:rgba(157,78,221,.35); }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin:26px 0; }}
.stat {{ background:var(--surface); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:16px; text-align:center; }}
.stat, .card, .commits {{ background:rgba(27,36,54,.88); backdrop-filter:blur(2px); }}
.stat .n {{ font-size:32px; font-weight:800; background:linear-gradient(135deg,var(--red),var(--accent)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.stat .l {{ color:var(--muted); font-size:12.5px; margin-top:2px; }}
#search {{ width:100%; max-width:520px; background:var(--surface); border:1px solid rgba(255,255,255,.12); border-radius:10px; color:var(--text); font-size:15px; padding:12px 16px; outline:none; }}
#search:focus {{ border-color:var(--accent); }}
.tagbar {{ margin:14px 0 4px; display:flex; flex-wrap:wrap; gap:8px; }}
.tag {{ display:inline-block; background:rgba(233,196,106,.12); color:var(--accent); border:none; border-radius:20px; padding:3px 10px; font-size:12px; cursor:pointer; }}
.tag.big {{ font-size:13px; padding:6px 14px; }}
.tag.active {{ background:var(--accent); color:#0d1321; font-weight:700; }}
.tag b {{ opacity:.7; font-weight:600; }}
section {{ margin-top:34px; }}
section h2 {{ font-size:21px; margin-bottom:14px; }}
.count {{ color:var(--muted); font-size:15px; font-weight:400; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); gap:14px; }}
.card {{ background:var(--surface); border:1px solid rgba(255,255,255,.07); border-radius:12px; overflow:hidden; text-decoration:none; color:var(--text); transition:transform .15s, border-color .15s; display:block; }}
.card:hover {{ transform:translateY(-3px); border-color:rgba(233,196,106,.5); }}
.card-top {{ height:4px; }}
.card-body {{ padding:16px; }}
.card-head {{ display:flex; gap:10px; align-items:center; font-size:11.5px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px; }}
.card h3 {{ font-size:17px; margin-bottom:8px; }}
.card p {{ color:var(--muted); font-size:13.5px; line-height:1.5; }}
.date {{ color:var(--muted); margin-left:auto; letter-spacing:0; }}
.status {{ background:rgba(42,157,143,.2); color:#2a9d8f; border-radius:6px; padding:1px 8px; }}
.meta {{ margin-top:10px; display:flex; flex-wrap:wrap; gap:6px; }}
.rel {{ color:var(--muted); font-size:12px; padding:3px 4px; }}
.commits {{ background:var(--surface); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:8px 18px; max-width:760px; }}
.commit {{ display:flex; gap:14px; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:13.5px; align-items:baseline; }}
.commit:last-child {{ border-bottom:none; }}
.commit code {{ color:var(--accent); }}
.commit .date {{ margin-left:0; white-space:nowrap; }}
.hidden {{ display:none; }}
footer {{ margin-top:44px; color:var(--muted); font-size:12.5px; }}
.pending-stat {{ text-decoration:none; border-color:rgba(233,196,106,.45) !important; }}
.pending-stat .n {{ background:none; -webkit-text-fill-color:var(--accent); color:var(--accent); }}
.pending-box {{ background:rgba(27,36,54,.88); border:1px solid rgba(233,196,106,.35); border-left:4px solid var(--accent); border-radius:12px; padding:12px 18px; max-width:760px; }}
.pending-box.clean {{ border-color:rgba(42,157,143,.4); border-left-color:#2a9d8f; color:var(--muted); }}
.pending-row {{ display:flex; gap:12px; align-items:baseline; padding:7px 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:13.5px; }}
.pending-row:last-of-type {{ border-bottom:none; }}
.pending-row code {{ color:var(--text); }}
.pstate {{ font-size:11.5px; white-space:nowrap; width:96px; }}
.pstate.modified {{ color:var(--accent); }}
.pstate.new {{ color:#7ddba3; }}
.pending-actions {{ display:flex; flex-wrap:wrap; gap:14px; align-items:center; padding-top:12px; margin-top:4px; border-top:1px solid rgba(255,255,255,.08); }}
.btn {{ background:var(--accent); color:#0d1321; font-weight:700; font-size:13px; text-decoration:none; border-radius:8px; padding:8px 14px; }}
.btn:hover {{ filter:brightness(1.1); }}
.hint {{ color:var(--muted); font-size:12.5px; }}
.hint code {{ color:var(--accent); }}
</style>
</head>
<body>
<canvas id="stars"></canvas>
<header>
<h1>🗄️ <span>Vault Dashboard</span></h1>
<div class="updated">Last updated: <b>{now}</b> · regenerates automatically when the vault changes</div>
{pages_html}
</header>

<div class="stats">
<div class="stat"><div class="n">{len(notes)}</div><div class="l">total notes</div></div>
<div class="stat"><div class="n">{counts.get("projects", 0)}</div><div class="l">projects</div></div>
<div class="stat"><div class="n">{counts.get("knowledge", 0)}</div><div class="l">knowledge notes</div></div>
<div class="stat"><div class="n">{counts.get("references", 0)}</div><div class="l">references</div></div>
<div class="stat"><div class="n">{counts.get("daily", 0)}</div><div class="l">daily notes</div></div>
<div class="stat"><div class="n">{len(commits)}</div><div class="l">recent commits</div></div>
<a class="stat pending-stat" href="#pending"><div class="n">{len(pending)}</div><div class="l">pending writes</div></a>
</div>

{pending_html}

<input id="search" type="search" placeholder="Search notes, tags, text…">
<div class="tagbar">{tag_html}</div>

{section_html}

<section><h2>🕐 Recent activity (git)</h2><div class="commits">{commit_html}</div></section>

<footer>Generated by .dashboard/generate.py · rules in CLAUDE.md · feed me daily</footer>

<script>
// --- twinkling starfield background ---
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');
let stars = [];
function seedStars() {{
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const n = Math.floor(canvas.width * canvas.height / 3800);
  stars = Array.from({{length: n}}, () => ({{
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 1.4 + 0.3,
    base: Math.random() * 0.55 + 0.25,          // base brightness
    amp: Math.random() * 0.45 + 0.15,           // twinkle depth
    speed: Math.random() * 1.6 + 0.3,           // twinkle speed
    phase: Math.random() * Math.PI * 2,
    hue: Math.random() < 0.12 ? '233,196,106' : (Math.random() < 0.08 ? '160,200,255' : '241,250,238')
  }}));
}}
function drawStars(t) {{
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (const s of stars) {{
    const a = Math.max(0, Math.min(1, s.base + Math.sin(t / 1000 * s.speed + s.phase) * s.amp));
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${{s.hue}},${{a.toFixed(3)}})`;
    ctx.fill();
    if (s.r > 1.2 && a > 0.75) {{               // glow on the brightest
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * 2.6, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${{s.hue}},${{(a * 0.12).toFixed(3)}})`;
      ctx.fill();
    }}
  }}
  requestAnimationFrame(drawStars);
}}
seedStars();
window.addEventListener('resize', seedStars);
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
  requestAnimationFrame(drawStars);
}} else {{
  drawStars(0); // static stars, no animation loop
}}

const search = document.getElementById('search');
let activeTag = null;
function apply() {{
  const q = search.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    const matchQ = !q || c.dataset.search.includes(q);
    const matchT = !activeTag || c.dataset.tags.split(',').includes(activeTag);
    c.classList.toggle('hidden', !(matchQ && matchT));
  }});
}}
search.addEventListener('input', apply);
document.querySelectorAll('.tag').forEach(t => t.addEventListener('click', e => {{
  e.preventDefault(); e.stopPropagation();
  activeTag = (activeTag === t.dataset.tag) ? null : t.dataset.tag;
  document.querySelectorAll('.tag').forEach(x => x.classList.toggle('active', x.dataset.tag === activeTag));
  apply();
}}));
</script>
</body>
</html>
'''


def main():
    notes = collect_notes()
    pending = git_pending()
    html_out = render(notes, pending)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_out)
    # keep the full-diff review page in sync so the dashboard's link is never stale
    review = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review.py")
    if os.path.exists(review):
        subprocess.run([sys.executable, review], cwd=VAULT, capture_output=True, timeout=15)
    print(f"dashboard.html regenerated: {len(notes)} notes, {len(pending)} pending write(s)")


if __name__ == "__main__":
    main()
