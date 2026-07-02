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
SECTIONS = ["daily", "knowledge", "projects", "references"]

TYPE_COLORS = {
    "daily": "#e9c46a", "note": "#2a9d8f", "project": "#e63946",
    "reference": "#457b9d", "index": "#8d99ae",
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


def render(notes):
    now = datetime.now().strftime("%A, %B %-d %Y · %H:%M:%S")
    tags = {}
    for n in notes:
        for t in n["tags"]:
            tags[t] = tags.get(t, 0) + 1
    counts = {s: sum(1 for n in notes if n["section"] == s) for s in SECTIONS}
    commits = git_log()

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
        ("projects", "🚀 Projects"), ("knowledge", "🧠 Knowledge"),
        ("references", "🔗 References"), ("daily", "📅 Daily notes"),
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
body {{ background:var(--bg); color:var(--text); font-family:'Helvetica Neue',Helvetica,Arial,sans-serif; padding:36px clamp(16px,4vw,60px) 80px; }}
header h1 {{ font-size:clamp(28px,4vw,44px); letter-spacing:-1px; }}
header h1 span {{ background:linear-gradient(135deg,var(--red),var(--accent)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.updated {{ color:var(--muted); font-size:14px; margin-top:6px; }}
.updated b {{ color:var(--accent); font-weight:600; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin:26px 0; }}
.stat {{ background:var(--surface); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:16px; text-align:center; }}
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
</style>
</head>
<body>
<header>
<h1>🗄️ <span>Vault Dashboard</span></h1>
<div class="updated">Last updated: <b>{now}</b> · regenerates automatically when the vault changes</div>
</header>

<div class="stats">
<div class="stat"><div class="n">{len(notes)}</div><div class="l">total notes</div></div>
<div class="stat"><div class="n">{counts.get("projects", 0)}</div><div class="l">projects</div></div>
<div class="stat"><div class="n">{counts.get("knowledge", 0)}</div><div class="l">knowledge notes</div></div>
<div class="stat"><div class="n">{counts.get("references", 0)}</div><div class="l">references</div></div>
<div class="stat"><div class="n">{counts.get("daily", 0)}</div><div class="l">daily notes</div></div>
<div class="stat"><div class="n">{len(commits)}</div><div class="l">recent commits</div></div>
</div>

<input id="search" type="search" placeholder="Search notes, tags, text…">
<div class="tagbar">{tag_html}</div>

{section_html}

<section><h2>🕐 Recent activity (git)</h2><div class="commits">{commit_html}</div></section>

<footer>Generated by .dashboard/generate.py · rules in CLAUDE.md · feed me daily</footer>

<script>
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
    html_out = render(notes)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"dashboard.html regenerated: {len(notes)} notes")


if __name__ == "__main__":
    main()
