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

    # optional wallpaper: drop any image into .dashboard/assets/ and it becomes the background
    wall, humans = None, []
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    if os.path.isdir(assets_dir):
        for fn in sorted(os.listdir(assets_dir)):
            ext = fn.lower().rsplit(".", 1)[-1]
            if fn.lower().startswith("prof") and ext in ("png", "webp"):
                humans.append(".dashboard/assets/" + fn)          # scene figures
            elif ext in ("jpg", "jpeg", "png", "webp") and not wall:
                wall = ".dashboard/assets/" + fn                  # first non-prof image = wallpaper
    body_class = "has-wall" if wall else ""
    if wall and humans:
        # real photographic scholars, cut out with transparent backgrounds
        figs = "".join(
            f'<div class="human human{i}"><img src="{html.escape(src)}" alt=""></div>'
            for i, src in enumerate(humans[:2], start=1))
        scene_html = f'<div class="scene" aria-hidden="true">{figs}</div>'
    elif wall:
        # fallback: simple scholar silhouettes if no photos are present
        prof_svg = ('<g class="prof"><path d="M50,205 L47,252 L56,252 L59,208 Z"/>'
                    '<path d="M62,205 L66,252 L75,252 L70,208 Z"/>'
                    '<path d="M58,54 C46,54 44,66 44,86 L39,210 L81,210 L76,86 C76,66 74,54 62,54 Z"/>'
                    '<circle cx="60" cy="39" r="15"/>'
                    '<path d="M46,86 C36,94 34,112 41,122" stroke="currentColor" stroke-width="9" stroke-linecap="round" fill="none"/>'
                    '<rect x="33" y="114" width="16" height="21" rx="2"/>'
                    '<g class="arm"><path d="M74,72 C89,60 99,44 105,30" stroke="currentColor" stroke-width="9" stroke-linecap="round" fill="none"/>'
                    '<rect x="99" y="19" width="17" height="13" rx="2"/></g></g>')
        scene_html = (f'<div class="scene" aria-hidden="true">'
                      f'<svg class="fig fig1" viewBox="0 0 130 260">{prof_svg}</svg>'
                      f'<svg class="fig fig2" viewBox="0 0 130 260">{prof_svg}</svg></div>')
    else:
        scene_html = ""
    wall_layers = (f'<div class="wall" style="background-image:url(\'{html.escape(wall)}\')"></div>'
                   '<div class="wall-tint"></div>') if wall else ""

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
    tracker_panel = ""
    if pages:
        pcards = "".join(
            f'<a class="pagecard" href="{html.escape(p)}"><span class="pagecard-t">{html.escape(l)}</span>'
            f'<span class="pagecard-go">Open</span></a>' for p, l in pages)
        tracker_panel = (f'<section class="tabpanel hidden" data-tab="__tracker__">'
                         f'<h2>Tracker <span class="count">{len(pages)}</span></h2>'
                         f'<div class="pagegrid">{pcards}</div></section>')

    if pending:
        rows = "".join(
            f'<div class="pending-row"><span class="pstate {st}">{"modified" if st == "modified" else "new"}</span>'
            f'<code>{html.escape(p)}</code></div>'
            for st, p in pending)
        pending_html = f'''<section id="pending"><h2>Pending review <span class="count">{len(pending)}</span></h2>
<div class="pending-box">
{rows}
<div class="pending-actions">
<button class="btn approve" data-push="0">Approve</button>
<button class="btn ghost approve" data-push="1">Approve &amp; push</button>
<a class="btn ghost" href="review.html">View diffs</a>
<span class="hint">or in terminal: <code>git add -A &amp;&amp; git commit</code></span>
</div>
</div></section>'''
    else:
        pending_html = ('<section id="pending"><h2>Pending review <span class="count">0</span></h2>'
                        '<div class="pending-box clean">Nothing awaiting approval — the vault is clean.</div></section>')

    def card(n):
        color = TYPE_COLORS.get(n["type"], "#2a9d8f")
        # keep the card face calm: at most 3 tags, no relation chips (relations still open in the note)
        shown = n["tags"][:3]
        extra = len(n["tags"]) - len(shown)
        tag_html = "".join(f'<span class="tag" data-tag="{html.escape(t)}">#{html.escape(t)}</span>' for t in shown)
        if extra > 0:
            tag_html += f'<span class="tag more">+{extra}</span>'
        status = f'<span class="status">{html.escape(n["status"])}</span>' if n["status"] else ""
        return f'''<a class="card" href="{html.escape(n["file"])}" data-search="{html.escape((n["title"] + " " + " ".join(n["tags"]) + " " + n["excerpt"]).lower())}" data-tags="{html.escape(",".join(n["tags"]))}">
<div class="card-body">
<div class="card-head"><span class="dot" style="background:{color}"></span><span class="type">{html.escape(n["type"])}</span>{status}<span class="date">{html.escape(n["created"])}</span></div>
<h3>{html.escape(n["title"])}</h3>
<p>{html.escape(n["excerpt"])}</p>
<div class="meta">{tag_html}</div>
</div></a>'''

    section_html = ""
    section_meta = [
        ("course", "Course"), ("projects", "Projects"), ("knowledge", "Knowledge"),
        ("decisions", "Decisions"), ("references", "References"), ("daily", "Daily notes"),
    ]
    present = []  # (key, label, count) for sections that actually have notes
    for key, label in section_meta:
        items = [n for n in notes if n["section"] == key]
        items.sort(key=lambda n: (n["created"], n["mtime"]), reverse=True)
        if not items:
            continue
        present.append((key, label, len(items)))
        cards = "\n".join(card(n) for n in items)
        section_html += (f'<section class="tabpanel" data-tab="{key}">'
                         f'<h2>{label} <span class="count">{len(items)}</span></h2>'
                         f'<div class="grid">{cards}</div></section>\n')

    # tab bar: one button per section (+ an "All" button), first section active by default
    tab_buttons = [f'<button class="tabbtn active" data-tab="__all__">All</button>']
    for key, label, cnt in present:
        tab_buttons.append(f'<button class="tabbtn" data-tab="{key}">{html.escape(label)}</button>')
    if pages:
        tab_buttons.append('<button class="tabbtn" data-tab="__tracker__">Tracker</button>')
    if pending:
        tab_buttons.append(f'<button class="tabbtn pendtab blink" data-scroll="pending">Pending · {len(pending)}</button>')
    tabs_html = f'<div class="tabnav">{"".join(tab_buttons)}</div>'

    # top stat squares — clickable ones filter to their section (same mechanism as the tabs)
    present_keys = {k for k, _, _ in present}

    def stat(n, label, tab=None):
        if tab and (tab == "__all__" or tab in present_keys):
            return f'<button class="stat stat-tab" data-tab="{tab}"><div class="n">{n}</div><div class="l">{label}</div></button>'
        return f'<div class="stat"><div class="n">{n}</div><div class="l">{label}</div></div>'

    stats_html = (
        '<div class="stats">'
        + stat(len(notes), "total notes", "__all__")
        + stat(counts.get("projects", 0), "projects", "projects")
        + stat(counts.get("knowledge", 0), "knowledge notes", "knowledge")
        + stat(counts.get("references", 0), "references", "references")
        + stat(counts.get("daily", 0), "daily notes", "daily")
        + stat(len(commits), "recent commits")
        + f'<a class="stat pending-stat" href="#pending"><div class="n">{len(pending)}</div><div class="l">pending writes</div></a>'
        + '</div>'
    )

    tag_html = "".join(
        f'<button class="tag big" data-tag="{html.escape(t)}">#{html.escape(t)} <b>{c}</b></button>'
        for t, c in sorted(tags.items(), key=lambda kv: -kv[1]))

    commit_html = "".join(
        f'<div class="commit"><span class="date">{html.escape(d)}</span><span>{html.escape(s)}</span></div>'
        for h, d, s in commits) or '<div class="commit"><span>no commits yet</span></div>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vault Dashboard</title>
<style>
:root {{ --bg:#0b0c10; --surface:#131419; --surface2:#181920; --text:#e9e6df; --muted:#8f8c85; --faint:#6a6862; --accent:#c8a86a; --line:rgba(255,255,255,.07); --line2:rgba(255,255,255,.11); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:linear-gradient(180deg,#0d0e13 0%,#08090c 60%,#060608 100%); background-attachment:fixed; color:var(--text); font-family:'Helvetica Neue',Helvetica,Arial,sans-serif; font-weight:300; padding:56px clamp(18px,6vw,84px) 100px; min-height:100vh; letter-spacing:.2px; }}
#stars {{ position:fixed; inset:0; width:100%; height:100%; z-index:-1; pointer-events:none; }}
/* wallpaper mode: a fixed cover image + a warm tint for legibility; cards turn to glass */
.wall {{ position:fixed; inset:0; z-index:-3; background-position:center; background-size:cover; background-repeat:no-repeat; transform:scale(1.06); transition:transform .35s ease-out; }}
.scene {{ position:fixed; inset:0; z-index:-1; pointer-events:none; overflow:hidden; }}
.fig {{ position:absolute; bottom:0; height:44vh; width:auto; color:rgba(20,14,8,.52); fill:currentColor; transition:transform .4s ease-out; }}
.fig1 {{ left:1.5%; height:47vh; }}
.fig2 {{ right:3%; height:38vh; transform:scaleX(-1); }}
.prof {{ transform-box:fill-box; animation:sway 7s ease-in-out infinite; }}
.fig2 .prof {{ animation-duration:8.5s; animation-delay:-2.5s; }}
.arm {{ transform-box:fill-box; transform-origin:74px 72px; animation:reach 7s ease-in-out infinite; }}
.fig2 .arm {{ animation-duration:8.5s; animation-delay:-3.5s; }}
@keyframes reach {{ 0%,100% {{ transform:rotate(8deg); }} 42% {{ transform:rotate(-34deg); }} 60% {{ transform:rotate(-34deg); }} }}
@keyframes sway {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-3px); }} }}
.human {{ position:absolute; bottom:0; transition:transform .4s ease-out; will-change:transform; pointer-events:auto; cursor:pointer; }}
.human1 {{ right:3%; height:60vh; z-index:1; }}
.human2 {{ left:2.5%; height:49vh; }}
.human::after {{ content:""; position:absolute; left:50%; bottom:1%; width:62%; height:22px; transform:translateX(-50%); background:radial-gradient(ellipse at center, rgba(0,0,0,.55), rgba(0,0,0,0) 72%); filter:blur(5px); pointer-events:none; z-index:-1; }}
.human img {{ position:relative; height:100%; width:auto; display:block; opacity:.86; filter:brightness(.58) contrast(1.05) sepia(.16) saturate(.88) drop-shadow(0 10px 20px rgba(0,0,0,.5)); animation:bob 7.5s ease-in-out infinite; transition:filter .35s ease, opacity .35s ease; }}
.human2 img {{ animation-duration:9s; animation-delay:-3s; }}
.human:hover img, .human.awake img {{ opacity:1; filter:brightness(.96) contrast(1.05) sepia(.04) saturate(1) drop-shadow(0 16px 28px rgba(0,0,0,.6)); }}
@keyframes bob {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-4px); }} }}
@media (max-width:820px) {{ .human1 {{ height:42vh; opacity:.7; }} .human2 {{ display:none; }} }}
@media (prefers-reduced-motion: reduce) {{ .prof, .arm, .human img {{ animation:none; }} }}
.wall-tint {{ position:fixed; inset:0; z-index:-2; background:linear-gradient(180deg, rgba(12,9,6,.50) 0%, rgba(11,8,5,.74) 48%, rgba(8,6,4,.90) 100%); }}
body.has-wall {{ background:#0a0806; }}
body.has-wall .stats, body.has-wall .stat {{ background:rgba(18,14,10,.60); backdrop-filter:blur(9px); -webkit-backdrop-filter:blur(9px); }}
body.has-wall .card, body.has-wall .pagecard, body.has-wall .commits, body.has-wall .pending-box, body.has-wall #search {{ background:rgba(18,14,10,.58); backdrop-filter:blur(9px); -webkit-backdrop-filter:blur(9px); }}
body.has-wall .card:hover, body.has-wall .pagecard:hover {{ background:rgba(26,20,14,.72); }}
body.has-wall .tabbtn, body.has-wall .tag {{ backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px); }}
header {{ margin-bottom:26px; }}
.wordmark {{ font-family:Georgia,'Times New Roman',serif; font-size:clamp(30px,4vw,46px); font-weight:400; letter-spacing:.5px; color:var(--text); }}
.updated {{ color:var(--faint); font-size:12.5px; margin-top:10px; letter-spacing:.4px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:1px; margin:0 0 40px; background:var(--line); border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
.stat {{ background:var(--surface); padding:22px 18px; text-align:center; }}
button.stat {{ font-family:inherit; color:var(--text); cursor:pointer; border:none; }}
.stat-tab {{ transition:background .2s; }}
.stat-tab:hover {{ background:var(--surface2); }}
.stat .n {{ font-family:Georgia,'Times New Roman',serif; font-size:34px; font-weight:400; color:var(--accent); }}
.stat .l {{ color:var(--muted); font-size:11px; margin-top:6px; text-transform:uppercase; letter-spacing:1.4px; }}
#search {{ width:100%; max-width:560px; background:var(--surface); border:1px solid var(--line2); border-radius:10px; color:var(--text); font-size:14px; font-family:inherit; padding:13px 17px; outline:none; transition:border-color .2s; }}
#search::placeholder {{ color:var(--faint); }}
#search:focus {{ border-color:var(--accent); }}
.controls {{ margin-top:8px; }}
.tagwrap {{ margin:20px 0 4px; }}
.tagwrap summary {{ cursor:pointer; color:var(--muted); font-size:12px; list-style:none; display:inline-flex; align-items:center; gap:9px; padding:6px 0; user-select:none; text-transform:uppercase; letter-spacing:1.2px; }}
.tagwrap summary::-webkit-details-marker {{ display:none; }}
.tagwrap summary::before {{ content:"+"; color:var(--accent); font-size:15px; display:inline-block; width:12px; }}
.tagwrap[open] summary::before {{ content:"–"; }}
.tcount {{ color:var(--faint); font-size:11px; }}
.tagbar {{ margin:14px 0 4px; display:flex; flex-wrap:wrap; gap:8px; }}
.tag {{ display:inline-block; background:transparent; color:var(--muted); border:1px solid var(--line2); border-radius:16px; padding:4px 12px; font-size:11.5px; cursor:pointer; transition:border-color .2s,color .2s; }}
.tag:hover {{ border-color:var(--accent); color:var(--accent); }}
.tag.big {{ font-size:12px; padding:6px 14px; }}
.tag.active {{ background:var(--accent); color:#12100b; border-color:var(--accent); }}
.tag.more {{ border-style:dashed; cursor:default; color:var(--faint); }}
.tag b {{ opacity:.55; font-weight:400; }}
.tabnav {{ display:flex; flex-wrap:wrap; gap:18px; margin:0 0 8px; padding-bottom:20px; border-bottom:1px solid var(--line); }}
.tabbtn {{ background:transparent; color:var(--muted); border:1px solid var(--line2); border-radius:24px; padding:10px 22px; font-size:13px; font-family:inherit; cursor:pointer; letter-spacing:.6px; transition:border-color .2s,color .2s; }}
.tabbtn:hover {{ border-color:var(--accent); color:var(--text); }}
.tabbtn b {{ opacity:.5; font-weight:400; margin-left:5px; }}
.tabbtn.active {{ background:var(--accent); color:#12100b; border-color:var(--accent); }}
.tabbtn.active b {{ opacity:.7; }}
.pendtab {{ border-color:var(--accent); color:var(--accent); }}
.pendtab.blink {{ animation:blinkgold 1.15s ease-in-out infinite; }}
@keyframes blinkgold {{
  0%,100% {{ background:transparent; color:var(--accent); border-color:var(--accent); box-shadow:0 0 0 rgba(200,168,106,0); }}
  50% {{ background:var(--accent); color:#12100b; border-color:var(--accent); box-shadow:0 0 16px rgba(200,168,106,.65); }}
}}
@media (prefers-reduced-motion: reduce) {{ .pendtab.blink {{ animation:none; background:var(--accent); color:#12100b; }} }}
section {{ margin-top:46px; }}
section h2 {{ font-family:Georgia,'Times New Roman',serif; font-size:18px; font-weight:400; letter-spacing:.5px; margin-bottom:20px; padding-bottom:12px; border-bottom:1px solid var(--line); text-transform:uppercase; letter-spacing:2px; color:var(--muted); }}
.count {{ color:var(--faint); font-size:13px; margin-left:6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:14px; overflow:hidden; text-decoration:none; color:var(--text); transition:border-color .2s,background .2s; display:block; }}
.card:hover {{ border-color:var(--line2); background:var(--surface2); }}
.card-body {{ padding:20px; display:flex; flex-direction:column; height:100%; }}
.card-head {{ display:flex; gap:9px; align-items:center; font-size:10.5px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px; color:var(--muted); }}
.dot {{ width:6px; height:6px; border-radius:50%; flex:0 0 auto; opacity:.85; }}
.type {{ color:var(--muted); }}
.card h3 {{ font-family:Georgia,'Times New Roman',serif; font-size:17px; font-weight:400; margin-bottom:9px; line-height:1.35; color:var(--text); }}
.card p {{ color:var(--muted); font-size:13px; font-weight:300; line-height:1.6; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
.card .meta {{ margin-top:auto; padding-top:16px; }}
.date {{ color:var(--faint); margin-left:auto; letter-spacing:.5px; }}
.status {{ background:transparent; color:var(--accent); border:1px solid var(--line2); border-radius:5px; padding:1px 8px; font-size:10px; }}
.meta {{ margin-top:10px; display:flex; flex-wrap:wrap; gap:7px; }}
.pagegrid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px; }}
.pagecard {{ display:flex; align-items:center; justify-content:space-between; gap:12px; background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:17px 19px; text-decoration:none; color:var(--text); transition:border-color .2s,background .2s; }}
.pagecard:hover {{ border-color:var(--accent); background:var(--surface2); }}
.pagecard-t {{ font-family:Georgia,'Times New Roman',serif; font-size:15px; }}
.pagecard-go {{ color:var(--accent); font-size:11px; text-transform:uppercase; letter-spacing:1.3px; flex:0 0 auto; }}
.commits {{ background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:6px 20px; max-width:820px; }}
.commit {{ display:flex; gap:16px; padding:12px 0; border-bottom:1px solid var(--line); font-size:13px; align-items:baseline; }}
.commit:last-child {{ border-bottom:none; }}
.commit code {{ color:var(--accent); font-size:12px; }}
.commit .date {{ margin-left:0; white-space:nowrap; color:var(--faint); }}
.hidden {{ display:none; }}
footer {{ margin-top:56px; color:var(--faint); font-size:11.5px; letter-spacing:.4px; }}
.pending-stat {{ text-decoration:none; }}
.pending-box {{ background:var(--surface); border:1px solid var(--line); border-left:2px solid var(--accent); border-radius:12px; padding:16px 22px; max-width:820px; }}
.pending-box.clean {{ border-left-color:var(--line2); color:var(--muted); }}
.pending-row {{ display:flex; gap:14px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--line); font-size:13px; }}
.pending-row:last-of-type {{ border-bottom:none; }}
.pending-row code {{ color:var(--text); font-size:12px; }}
.pstate {{ font-size:10px; white-space:nowrap; width:74px; text-transform:uppercase; letter-spacing:1.2px; color:var(--muted); }}
.pstate.modified {{ color:var(--accent); }}
.pstate.new {{ color:var(--muted); }}
.pending-actions {{ display:flex; flex-wrap:wrap; gap:16px; align-items:center; padding-top:16px; margin-top:6px; border-top:1px solid var(--line); }}
.btn {{ background:var(--accent); color:#12100b; font-size:12px; font-family:inherit; text-decoration:none; border:1px solid var(--accent); border-radius:7px; padding:9px 16px; letter-spacing:.4px; cursor:pointer; }}
.btn:hover {{ filter:brightness(1.08); }}
.btn.ghost {{ background:transparent; color:var(--accent); }}
.btn.ghost:hover {{ background:rgba(200,168,106,.12); filter:none; }}
.btn:disabled {{ opacity:.6; cursor:default; }}
.hint {{ color:var(--faint); font-size:12px; }}
.hint code {{ color:var(--muted); }}
</style>
</head>
<body class="{body_class}">
{wall_layers}
{scene_html}
<canvas id="stars"></canvas>
<header>
<div class="wordmark">The Vault</div>
<div class="updated">Updated {now} · regenerates automatically when the vault changes</div>
</header>

{tabs_html}

<div class="controls">
<input id="search" type="search" placeholder="Search notes, tags, text…">
</div>

<details class="tagwrap">
<summary>Filter by tag <span class="tcount">{len(tags)}</span></summary>
<div class="tagbar">{tag_html}</div>
</details>

{pending_html}

{section_html}
{tracker_panel}

<section><h2>Recent activity</h2><div class="commits">{commit_html}</div></section>

<footer>Generated by .dashboard/generate.py · rules in CLAUDE.md</footer>

<script>
// --- twinkling starfield background ---
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');
let stars = [];
function seedStars() {{
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const n = Math.floor(canvas.width * canvas.height / 5200);
  stars = Array.from({{length: n}}, () => ({{
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 0.8 + 0.25,              // small
    base: Math.random() * 0.32 + 0.16,          // visible over the wallpaper tint
    amp: Math.random() * 0.30 + 0.12,           // gentle twinkle
    speed: Math.random() * 1.2 + 0.3,           // twinkle speed
    phase: Math.random() * Math.PI * 2,
    hue: Math.random() < 0.55 ? '201,168,106' : '224,190,120'   // gold tones, synced to the gilt
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
    if (s.r > 0.7 && a > 0.6) {{                // soft gold glow on the brightest
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * 3.2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${{s.hue}},${{(a * 0.14).toFixed(3)}})`;
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

// --- interactive: background + scholars drift with the cursor (parallax) ---
const wallEl = document.querySelector('.wall');
const figs = document.querySelectorAll('.fig, .human');
if ((wallEl || figs.length) && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
  let raf = null;
  window.addEventListener('mousemove', e => {{
    if (raf) return;
    raf = requestAnimationFrame(() => {{
      raf = null;
      const cx = e.clientX / window.innerWidth - 0.5;
      const cy = e.clientY / window.innerHeight - 0.5;
      if (wallEl) wallEl.style.transform = `scale(1.06) translate(${{(-cx*16).toFixed(1)}}px, ${{(-cy*11).toFixed(1)}}px)`;
      figs.forEach((f, i) => {{
        const depth = (i + 1) * 8;
        const base = f.classList.contains('fig2') ? 'scaleX(-1) ' : '';
        f.style.transform = base + `translateX(${{(cx*depth).toFixed(1)}}px)`;
      }});
    }});
  }});
}}

// click a scholar to keep them "awake" (fully lit)
document.querySelectorAll('.human').forEach(h => h.addEventListener('click', () => h.classList.toggle('awake')));

// approve pending writes from the page (needs the local approve server running)
async function approve(push, btn) {{
  const original = btn.textContent;
  document.querySelectorAll('.approve').forEach(b => b.disabled = true);
  btn.textContent = push === '1' ? 'Committing & pushing…' : 'Committing…';
  const served = location.protocol === 'http:' || location.protocol === 'https:';
  const base = served ? '' : 'http://127.0.0.1:8791';
  try {{
    const res = await fetch(base + '/api/approve?push=' + push, {{
      method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: '{{}}'
    }});
    const data = await res.json();
    if (data.ok) {{ btn.textContent = 'Approved ✓'; setTimeout(() => location.reload(), 800); }}
    else {{ alert('Approve failed:\\n\\n' + (data.message || 'unknown error')); reset(original); }}
  }} catch (e) {{
    alert('The approve server is not running.\\n\\nStart it in a terminal:\\n  python3 .dashboard/serve.py\\n\\nthen open  http://127.0.0.1:8791/dashboard.html');
    reset(original);
  }}
  function reset(txt) {{ document.querySelectorAll('.approve').forEach(b => b.disabled = false); btn.textContent = txt; }}
}}
document.querySelectorAll('.approve').forEach(b => b.addEventListener('click', () => approve(b.dataset.push, b)));

const search = document.getElementById('search');
let activeTag = null;
let activeSection = '__all__';
function apply() {{
  const q = search.value.toLowerCase();
  // 1) show only the chosen tab's panel (unless "All"), and reveal panels that hold a search/tag hit
  document.querySelectorAll('.tabpanel').forEach(p => {{
    const t = p.dataset.tab;
    const onTab = (t === '__tracker__') ? (activeSection === '__tracker__')
                                        : (activeSection === '__all__' || t === activeSection);
    p.classList.toggle('hidden', !onTab);
  }});
  // 2) filter the cards inside the visible panels by search + tag
  document.querySelectorAll('.card').forEach(c => {{
    const matchQ = !q || c.dataset.search.includes(q);
    const matchT = !activeTag || c.dataset.tags.split(',').includes(activeTag);
    c.classList.toggle('hidden', !(matchQ && matchT));
  }});
}}
search.addEventListener('input', apply);
function activateTab(key, scroll) {{
  activeSection = key;
  document.querySelectorAll('.tabbtn').forEach(x => x.classList.toggle('active', x.dataset.tab === key));
  apply();
  if (scroll) {{
    const nav = document.querySelector('.tabnav');
    if (nav) nav.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
}}
document.querySelectorAll('.tabbtn').forEach(b => b.addEventListener('click', () => {{
  if (b.dataset.scroll) {{
    const el = document.getElementById(b.dataset.scroll);
    if (el) el.scrollIntoView({{ behavior:'smooth', block:'start' }});
    return;
  }}
  activateTab(b.dataset.tab, false);
}}));
document.querySelectorAll('.stat-tab').forEach(s => s.addEventListener('click', () => activateTab(s.dataset.tab, true)));
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
