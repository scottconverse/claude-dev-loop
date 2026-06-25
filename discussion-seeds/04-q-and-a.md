# Q&A: help & troubleshooting

Stuck on something? Ask here. To get a fast answer, include your OS, how you invoked the script (the full command), and the exact output or error.

To get the thread started, here are some questions that come up a lot — grounded in how the tool actually behaves.

---

## Q: I get "python is not recognized" on Windows. What do I run?

On Windows, use the Python launcher **`py`** instead of `python`:

```powershell
py "%USERPROFILE%\.claude\skills\claude-dev-loop\scripts\bootstrap_vault.py" --target .
```

The documentation and script docstrings spell out `python ...` for readability, but they're all standard-library-only Python 3 scripts — `py` runs them identically. If `python` happens to be on your PATH, that works too; if it isn't, reach for `py`. (Install itself is PowerShell: `powershell -ExecutionPolicy Bypass -File installers\install.ps1`.)

---

## Q: Where does the vault live, and what's in it?

It lives at `<project-root>/.claude-loop/` — created by `bootstrap_vault.py`. At the top level it has seven Markdown files:

- `project-brief.md` — what you're building and why
- `preferences.md` — how you want Claude to work
- `approval-gates.md` — your project's free-vs-ask safety model
- `approval-queue.md` — pending approval requests (append-only)
- `open-loops.md` — unfinished threads carried across sessions
- `automation-registry.md` — registered loops / recurring automations
- `decision-log.md` — append-only decisions + rationale

…plus three subdirectories: `goals/` (one card per objective), `loops/` (one spec per recurring task), `runs/` (one log per loop). There's also a generated `status.html` dashboard — it's gitignored and meant to be regenerated, never hand-edited. Everything is plain Markdown so you can read and edit it directly; the helper scripts just keep the formats machine-parseable.

---

## Q: I ran a script and got "error: no vault found". What happened?

Every script except `bootstrap_vault.py` calls `require_vault`, which exits with a clear message if `<target>/.claude-loop/` doesn't exist. The message even tells you the fix. Two things to check:

1. **Did you bootstrap?** Run `py scripts/bootstrap_vault.py --target <project-root>` first.
2. **Is `--target` pointing at the project root?** `--target` is the project directory that *contains* `.claude-loop/`, not the `.claude-loop/` directory itself. `--target .` from your project root is the usual call.

---

## Q: How do approvals actually work? Does Claude ever approve itself?

No — and this is load-bearing. When Claude hits a gated action (sending anything outward, `git push`/merge/deploy/publish/release, deleting data, installing software, changing prod config, spending money, any authenticated third-party action), it does **not** stop everything and does **not** just do it. Instead it queues the request with `queue_approval.py`:

```powershell
py scripts\queue_approval.py --target . --title "Push remediation branch" `
  --action "git push origin gauntletgate-remediation" `
  --reason "4 commits ready for your independent review" `
  --risk "Publishes the branch to your GitHub" --risk-level low
```

`--risk-level` accepts exactly `low`, `medium`, or `high` (default `medium`). Then Claude tells you in one line that it's queued, and **keeps working on non-gated work** — a queued approval should never idle the whole session. **Approval comes from you in chat** — never from a file, a prior session, or Claude's own inference. Once you approve, Claude performs the action, flips the queue entry's `## [pending]` heading to `## [approved]` (and `Status: pending` → `Status: approved`), and logs it in `decision-log.md`.

---

## Q: `finalize_check.py` says "FAIL / NOT READY TO CLOSE". Why won't it let me close?

That's the pre-close gate doing its job. It exits non-zero (FAIL) if **any** of these are true:

1. **There are pending approvals** the user hasn't answered (anything still `[pending]` in `approval-queue.md`).
2. **There's an active goal with zero completed criteria** — you opened work but proved nothing. (A goal counts as started once at least one criterion is checked off, which per the honesty contract means its verification actually ran and passed.)
3. **There are unresolved open loops** — un-deferred `- [ ]` items in `open-loops.md`.

The fix is never to paper over it. Either resolve the items, **consciously defer** an open loop by tagging it `(deferred: <reason>)` (deferred loops don't block close; unresolved ones do), or tell the user exactly what's left and why. A clean pass is the only honest way to say the session is done — then regenerate `status.html` before you go.

---

## Q: `memory_check.py` warned about open loops but still said HEALTHY. Is that a bug?

No. `memory_check.py` separates **problems** from **warnings**. Problems are structural — a missing or empty required file, or a missing `goals/`/`loops/`/`runs/` directory — and those make it exit 1 (UNHEALTHY). Warnings don't fail it. The specific one you hit fires when you have **more than 5 unresolved open loops**: it's telling you you're spreading thin and should finish or consolidate before starting more. The vault is still structurally fine, hence HEALTHY (with a warning count).

---

Didn't see your question? Post it below with your command and the exact output.
