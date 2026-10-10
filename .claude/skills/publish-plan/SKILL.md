---
name: publish-plan
description: Put a plan's web page online on ht-ml.app behind a password, or update a page already online, and hand the user the link and password. Use when the user asks to publish, share, host, send to a customer, update the live page, or find a lost link or password.
---

# Publish a plan page

Goal: the page is live at its link, the user has the link and password, and `plans/<name>/.publish.json` records it.

1. **Pick the plan.** List folders in `plans/`. If the user didn't say which customer, ask with the folder names as choices.
2. **Rebuild and check.** `uv run tools/build.py plans/<name>`, then `uv run tools/smoke.py plans/<name>`. Fix anything it reports as `errors:` before going on.
3. **First time for this plan?** (no `plans/<name>/.publish.json`). Say once, plainly: "This puts the page on ht-ml.app, a free outside hosting service. It will be locked with a password. Once a page is up it can be changed but not deleted, and ht-ml.app's terms let them keep what's uploaded. OK to go ahead?" Wait for a yes.
4. **Publish.** `uv run tools/publish.py plans/<name>`. It creates the page with a new password the first time, and updates the same link (same password) after that. For the LED contractor sheet: add `--file share/led-power.html --as led`. To change a password someone shouldn't have anymore: add `--new-password`.
5. **Hand it over.** Give the user the link and the password from the output, and tell them:
   - send the link and the password to their customer in **two separate messages**;
   - the customer opens the link, types the password once, and sees the plan; it works on phones;
   - when the plan changes, say "publish again" and the same link updates.
6. **Commit.** `git add -A` and `git commit -m "<name>: published"` (`.publish.json` is ignored and stays out of git).

Lost link or password: `uv run tools/publish.py plans/<name> --show`. A plan published before this kit existed may show `(none saved)` for the password; offer `--new-password` to set a fresh one, and remind the user that the old password stops working for everyone they sent it to.

If ht-ml.app refuses the page (HTTP 422, safety scan), read its message, fix the page, and publish again. If the update key is refused (401/403), the record in `.publish.json` is wrong or from another copy of this folder: tell the user, and offer to publish a new page instead (new link and password).
