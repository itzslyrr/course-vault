#!/usr/bin/env python3
"""Local approve server for the vault dashboard.

Serves the vault over http://127.0.0.1:8787 and exposes POST /api/approve, which
stages + commits (optionally pushes) the pending changes, then regenerates the
dashboard so the pending tab clears. Localhost only — nothing is exposed to the network.

Run:  python3 .dashboard/serve.py
Then: open http://127.0.0.1:8787/dashboard.html
"""
import http.server
import socketserver
import subprocess
import os
import sys
import json
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
PORT = 8791


def git(args):
    return subprocess.run(["git", *args], cwd=VAULT, capture_output=True, text=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=VAULT, **k)

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/approve":
            return self._json(404, {"ok": False, "message": "unknown endpoint"})
        push = urllib.parse.parse_qs(parsed.query).get("push", ["0"])[0] == "1"
        # drain any request body
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            self.rfile.read(length)

        status = git(["status", "--porcelain"]).stdout.strip()
        if not status:
            return self._json(200, {"ok": True, "message": "Nothing to approve — already clean."})

        git(["add", "-A"])
        commit = git(["commit", "-m", "Approve pending vault changes (from dashboard)"])
        if commit.returncode != 0:
            return self._json(500, {"ok": False, "message": commit.stderr or commit.stdout})
        out = commit.stdout.strip()

        if push:
            pushed = git(["push", "origin", "HEAD"])
            out += "\n\n" + ((pushed.stderr or pushed.stdout).strip())
            if pushed.returncode != 0:
                # committed fine, push failed — report but don't treat as full failure
                out = "Committed locally, but push failed:\n" + out

        # regenerate so the dashboard reflects the now-clean state
        subprocess.run([sys.executable, os.path.join(HERE, "generate.py")],
                       cwd=VAULT, capture_output=True)
        return self._json(200, {"ok": True, "message": out})

    def log_message(self, *a):
        pass  # quiet


def main():
    os.chdir(VAULT)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Approve server running → http://127.0.0.1:{PORT}/dashboard.html")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
