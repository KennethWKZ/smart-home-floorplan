"""Check this laptop has what the project needs. Prints one line per check and a fix for anything missing.

usage: uv run tools/doctor.py
"""
import importlib.util, pathlib, platform, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems = 0


def check(ok, label, fix=""):
    global problems
    print(("OK    " if ok else "FIX   ") + label + ("" if ok or not fix else f"\n      -> {fix}"))
    problems += not ok


def run(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


print(f"System: {platform.system()} {platform.release()} ({platform.machine()}), Python {platform.python_version()}")
check(sys.version_info >= (3, 11), "Python 3.11 or newer", "run commands through uv: uv run tools/doctor.py")
check(bool(shutil.which("uv")), "uv (runs the Python tools)", "see .claude/skills/setup/SKILL.md, step 2")
check(bool(shutil.which("git")), "git (keeps history of your plans)", "see .claude/skills/setup/SKILL.md, step 3")
if shutil.which("git"):
    check(bool(run("git", "config", "user.name")) and bool(run("git", "config", "user.email")),
          "git knows your name and email", 'git config --global user.name "Your Name"; git config --global user.email you@example.com')
check(importlib.util.find_spec("pymupdf") is not None, "PyMuPDF (reads the PDF drawings)", "uv sync")
pw = importlib.util.find_spec("playwright") is not None
check(pw, "Playwright (makes PNG/SVG exports and screenshots)", "uv sync")
if pw:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            p.chromium.launch().close()
        check(True, "Chromium for Playwright")
    except Exception as e:  # missing browser or, on Linux, missing system libraries
        fix = "uv run playwright install chromium"
        if platform.system() == "Linux":
            fix += "   (if it still fails: uv run playwright install-deps chromium, which asks for your password)"
        check(False, f"Chromium for Playwright ({str(e).splitlines()[0][:80]})", fix)
plans = sorted(p.name for p in (ROOT / "plans").iterdir() if (p / "plan.json").is_file())
check(bool(plans), f"plans found: {', '.join(plans) or 'none'}")
print("\nAll good." if not problems else f"\n{problems} thing(s) to fix.")
sys.exit(1 if problems else 0)
