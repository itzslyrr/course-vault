#!/usr/bin/env python3
"""Render all uncommitted vault changes into review.html — the pre-approval desk.

Usage:  python3 .dashboard/review.py   (from the vault root, then open review.html)

Shows every pending write: modified files as colored diffs, new files in full.
The page is read-only by design — approval stays in the terminal (git commit).
review.html is gitignored: the review sheet itself never enters history.
"""
import html
import os
import subprocess

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(VAULT, "review.html")

SKIP = {"dashboard.html", "review.html", ".DS_Store"}


def run(*args):
    return subprocess.run(["git", *args], cwd=VAULT, capture_output=True, text=True).stdout


def diff_to_html(diff):
    lines = []
    for line in diff.splitlines():
        esc = html.escape(line)
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(f'<div class="add">{esc}</div>')
        elif line.startswith("-") and not line.startswith("---"):
            lines.append(f'<div class="del">{esc}</div>')
        elif line.startswith("@@"):
            lines.append(f'<div class="hunk">{esc}</div>')
        else:
            lines.append(f'<div class="ctx">{esc}</div>')
    return "\n".join(lines)


def main():
    status = run("status", "--porcelain").splitlines()
    modified, untracked = [], []
    for line in status:
        code, path = line[:2], line[3:].strip().strip('"')
        base = os.path.basename(path)
        if base in SKIP:
            continue
        if code.strip() == "??":
            if os.path.isdir(os.path.join(VAULT, path)):
                for root, _, files in os.walk(os.path.join(VAULT, path)):
                    for f in sorted(files):
                        if f not in SKIP:
                            untracked.append(os.path.relpath(os.path.join(root, f), VAULT))
            else:
                untracked.append(path)
        else:
            modified.append(path)

    cards = ""
    for path in modified:
        cards += (f'<section class="card"><h2>✏️ modified · {html.escape(path)}</h2>'
                  f'<pre>{diff_to_html(run("diff", "--", path))}</pre></section>\n')
    for path in untracked:
        try:
            with open(os.path.join(VAULT, path), encoding="utf-8") as f:
                body = f.read()
        except (UnicodeDecodeError, OSError):
            body = "(binary or unreadable — review in terminal)"
        content = "\n".join(f'<div class="add">+{html.escape(l)}</div>' for l in body.splitlines())
        cards += (f'<section class="card"><h2>🆕 new file · {html.escape(path)}</h2>'
                  f'<pre>{content}</pre></section>\n')

    n = len(modified) + len(untracked)
    verdict = (f"{n} pending write{'s' if n != 1 else ''} awaiting your review"
               if n else "Nothing pending — the vault is clean ✅")

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Vault — Pending Review</title>
<style>
 body {{ background:#0f1420; color:#dde3ee; font:15px/1.5 -apple-system,sans-serif; max-width:900px; margin:32px auto; padding:0 16px; }}
 h1 {{ font-size:22px; }} .verdict {{ color:#e9c46a; margin-bottom:24px; }}
 .card {{ background:#1b2436; border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:14px 18px; margin-bottom:18px; }}
 .card h2 {{ font-size:15px; margin:0 0 10px; color:#8ecae6; }}
 pre {{ background:#0f1420; border-radius:8px; padding:10px; overflow-x:auto; font:12.5px/1.45 ui-monospace,monospace; }}
 .add {{ color:#7ddba3; }} .del {{ color:#ef7a85; }} .hunk {{ color:#e9c46a; }} .ctx {{ color:#7a8499; }}
 .how {{ background:#1b2436; border-left:3px solid #2a9d8f; border-radius:8px; padding:12px 16px; font-size:13.5px; }}
 code {{ color:#8ecae6; }}
</style></head><body>
<h1>⚖️ Pending review — the doorway</h1>
<p class="verdict">{verdict}</p>
{cards}
<div class="how"><b>To approve:</b> in the terminal, from the vault —<br>
<code>git add -A &amp;&amp; git commit -m "your message"</code> · then <code>git push</code><br>
<b>To reject a file:</b> <code>git checkout -- &lt;file&gt;</code> (modified) or delete it (new).<br>
This page only reads. Nothing lands until you commit.</div>
</body></html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"review.html regenerated: {n} pending write(s)")


if __name__ == "__main__":
    main()
