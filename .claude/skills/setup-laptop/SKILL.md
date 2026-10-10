---
name: setup-laptop
description: First-time setup of this project on the user's laptop (macOS, Windows or Linux) - installs uv, git, Python libraries and the Chromium browser, then opens the example plan. Use when the user asks to set up, install, get started, or when tools/doctor.py reports anything to fix.
---

# Set up this laptop

Goal: `uv run tools/doctor.py` prints `All good.` and the example plan is open in the user's browser. Work through the steps in order; skip any step whose check already passes. Talk to the user as `CLAUDE.md` describes: you run the commands, they only click pop-ups, type passwords and log in.

**Commands that need their password** go through them. In the terminal app, they type the command into Claude with a leading `!` (`! sudo ...`) and press Enter. The VS Code chat panel has no `!`: there, they open **Terminal → New Terminal** in VS Code, paste the command without the `!`, and press Enter. Give them the version that matches where they are talking to you.

## 1. Find out where you are

Check the operating system (`uname -s` in bash; `$env:OS` in PowerShell) and that the current folder is the repo root (it holds `CLAUDE.md` and `plans/`). Tell the user in one sentence: "You're on a Mac/Windows/Linux laptop; I'll install three free tools: uv, git and a browser engine."

## 2. uv (runs the Python tools; brings its own Python)

Check: `uv --version`. If missing, install it:

- macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

The installer puts uv in `~/.local/bin` (Windows: `%USERPROFILE%\.local\bin`). The current session may not see it yet: call it by that full path for the rest of setup, and at the end tell the user to close and reopen the terminal before the next session.

## 3. git (keeps a history of every change, so nothing is lost)

Check: `git --version`. If missing:

- macOS: run `xcode-select --install`. A window pops up: tell the user to click **Install**, then **Agree**, and wait (5-15 minutes) until it says the software was installed.
- Windows: `winget install --id Git.Git -e --source winget`. Tell the user to click **Yes** on the "allow this app to make changes" pop-up. Reopen the terminal afterwards if `git` is still not found.
- Linux: it needs their computer password, so hand them `sudo apt install -y git` (Fedora: `sudo dnf install -y git`) as a password command (see above).

Then check `git config user.name` and `git config user.email`. If either is empty, ask the user for the name and email they want on their changes and set them with `git config --global`.

If the folder is not a git repository yet (`git status` fails, e.g. it came from a ZIP download), run `git init`, `git add -A` and `git commit -m "Start from the smart-home floorplan kit"`.

## 4. Python libraries

Run `uv sync`. uv downloads Python itself when the laptop has none; the first run takes a minute or two.

## 5. Browser engine for exports and checks

Run `uv run playwright install chromium` (about 150 MB). On Linux, if `tools/doctor.py` still reports Chromium failing, the system libraries are missing: hand them `uv run playwright install-deps chromium` as a password command (see above).

## 6. Check

Run `uv run tools/doctor.py`. Fix each `FIX` line with its hint and run it again until it prints `All good.`

## 7. Show the example

Run `uv run tools/build.py plans/example`, then open `plans/example/index.html` in their browser (macOS `open`, Windows `start ""`, Linux `xdg-open`). Tell them what they are looking at: a real apartment's plan (names removed) with every smart device placed; the tabs along the top switch between Zigbee, Thread, Wi-Fi, IR, LED power and switch circuits; devices can be dragged.

Finish with two lines: setup is done, and next time they open a terminal in this folder, type `claude`, and say "make a new plan for a customer" to start their own.
