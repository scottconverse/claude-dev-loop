# Show and tell: share your vault

This is the place to show off what you've built with claude-dev-loop. Vaults, goal cards, loop specs, run logs, a screenshot of your `status.html` dashboard — all welcome. Seeing how other people structure their work is the fastest way to get better at structuring your own.

## What's interesting to share

- **Your `project-brief.md`** (redacted as needed) — how you framed what you're building and your definition of success.
- **A goal card you're proud of** — especially the **Verification** section. The interesting part of a goal isn't the objective, it's the exact step or command that proves each criterion. Show us the proof you wired up.
- **A loop spec** — the trigger / action / verifier / budget / stop. A good verifier is genuinely runnable, and that's where the craft lives. (There's a whole **Loop patterns** thread on what separates a real loop from a wish.)
- **A run log** (`runs/<slug>-runs.md`) with real failures in it. A run log that's all `PASS` and never a single `FAIL` is a red flag, not a trophy — so the honest, messy ones are the most useful to see.
- **Your `status.html` dashboard** — generate it with `py scripts/loop_status.py --target . --html` and screenshot it. The dark-themed dashboard shows every goal (status badge + criteria progress bar), every loop (status, run count, last verifier result), pending approvals, and open loops.

## A nice format for a post

To make your share easy to learn from, consider including:

1. **One line on the project** — what is it, what stack.
2. **The artifact** — paste the goal card / loop spec / run entry, or the dashboard screenshot.
3. **What worked** — did the honesty contract catch you about to overclaim? Did a loop's stop condition save you from spinning? Did `finalize_check.py` block a close you thought was clean?
4. **What you'd change** — rough edges are great fuel for the **Ideas** thread.

## A couple of prompts if you're not sure where to start

- What's the smallest loop you set up that paid for itself? (A nightly test gate? A "regenerate the dashboard before close" loop?)
- How did you tune `approval-gates.md` for *your* project — what did you add to the default "ask first" list?
- Has the open-loops mechanism ever caught you spreading too thin? (`memory_check.py` warns once you pass 5 unresolved open loops.)

Paste away. Bonus points for showing the parts that didn't go smoothly — that's where everyone learns the most.
