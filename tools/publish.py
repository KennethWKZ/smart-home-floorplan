"""Publish a plan page on ht-ml.app (https://ht-ml.app) and keep its login details in plans/<name>/.publish.json.

First run creates a password-protected page and prints its link and password.
Later runs update the same link in place; the password stays the same.

usage:
  uv run tools/publish.py plans/<name>                  publish or update index.html
  uv run tools/publish.py plans/<name> --file share/led-power.html --as led
                                                        publish another page; --as names its record
  uv run tools/publish.py plans/<name> --new-password   update and switch to a new password
  uv run tools/publish.py plans/<name> --show           print the link and password, publish nothing

.publish.json holds the update_key: whoever has it can replace the page, and ht-ml.app cannot recover it.
It is git-ignored; never commit it, paste it into chat, or share it. Pages can't be deleted on ht-ml.app.
"""
import argparse, json, os, pathlib, re, secrets, sys, urllib.error, urllib.request
from datetime import datetime, timezone

API = os.environ.get("HTML_APP_API", "https://api.ht-ml.app/v1").rstrip("/")


def call(method, path, body, key=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method=method,
                                 headers={"Content-Type": "application/json", "User-Agent": "smart-home-floorplan/1"})
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        hint = {401: "the saved update_key was refused", 403: "the saved update_key does not match this page",
                422: "ht-ml.app's safety scan rejected the HTML; its message is above",
                429: "too many requests; wait a minute and try again"}.get(e.code, "")
        sys.exit(f"ht-ml.app said HTTP {e.code}: {detail}\n{hint}".rstrip())
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach ht-ml.app ({e.reason}). Check the internet connection and try again.")


def password_line(rec):
    if rec.get("password"):
        return rec["password"]
    if rec.get("public"):
        return "(none: anyone with the link can open it)"
    return "(unchanged, but not saved in this folder; --new-password sets a fresh one)"


def main():
    ap = argparse.ArgumentParser(description="Publish a plan page on ht-ml.app")
    ap.add_argument("plan", help="plan folder, e.g. plans/example")
    ap.add_argument("--file", default="index.html", help="page inside the plan folder (default index.html)")
    ap.add_argument("--as", dest="name", default="main", help="record name when a plan has several pages (default main)")
    ap.add_argument("--new-password", action="store_true", help="switch the page to a new generated password")
    ap.add_argument("--public", action="store_true", help="create the page without a password (anyone with the link can open it)")
    ap.add_argument("--show", action="store_true", help="print the saved link and password only")
    a = ap.parse_args()

    root = pathlib.Path(a.plan).resolve()
    rec_path = root / ".publish.json"
    store = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.is_file() else {}
    if "site_id" in store:                      # single-record format: treat it as the "main" page
        store = {"main": store}
    rec = store.get(a.name)

    if a.show:
        if not rec:
            sys.exit(f"{root.name} has no published '{a.name}' page yet.")
        print(f"link: {rec['url']}\npassword: {password_line(rec)}")
        return

    page = root / a.file
    if not page.is_file():
        sys.exit(f"{page} not found. Build it first: uv run tools/build.py {a.plan}")
    html = page.read_text(encoding="utf-8")
    local = sorted({m for m in re.findall(r'(?:src|href)="([^"#:]+\.(?:png|jpe?g|svg|webp|gif|css|js))"', html)})
    if local:
        print("warning: the page points at local files that ht-ml.app won't have:", ", ".join(local[:8]))

    if rec and a.public:
        sys.exit("--public only applies when creating a page; ht-ml.app can't make a private page public again.")
    if rec:
        body = {"html_content": html}
        if a.new_password:
            body["password"] = rec["password"] = secrets.token_urlsafe(9)
        call("PUT", f"/sites/{rec['site_id']}", body, key=rec["update_key"])
        action = "updated"
    else:
        password = None if a.public else secrets.token_urlsafe(9)
        body = {"html_content": html} | ({"password": password} if password else {})
        r = call("POST", "/sites", body)
        rec = {"site_id": r["site_id"], "url": r["url"], "update_key": r["update_key"], "password": password, "public": a.public}
        action = "created"
    rec["file"] = a.file
    rec["published_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    store[a.name] = rec
    rec_path.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")

    print(f"{action}: {rec['url']}")
    print(f"password: {password_line(rec)}")
    print(f"details saved in {rec_path.relative_to(root.parent.parent) if root.parent.parent in rec_path.parents else rec_path} (private, not in git)")


if __name__ == "__main__":
    main()
