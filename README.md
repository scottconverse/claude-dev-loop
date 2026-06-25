# claude-dev-loop

A durable development-workflow operating system for **Claude Code in the Cowork Desktop app
(Code tab)**. It gives Claude a persistent project memory (the **vault**), a way to declare and
verify work (**goals** and **loops**), an honest record of what happened (**runs** and the
**decision log**), and hard rules about what may be done freely versus what must wait for human
approval (**the safety model** and the **approval queue**).

It exists to kill one failure mode: an assistant that *claims* work is done, *claims* something
is verified, or quietly works around a missing dependency and calls the result finished. The
core skill (`CLAUDE.md`) opens with an **honesty contract** that makes "verified" mean *proven in
the same turn, with evidence* — or else say "not verified."

Modeled on [`scottconverse/codex-dev-loop`](https://github.com/scottconverse/codex-dev-loop),
rebuilt native to Claude Code instead of OpenAI Codex.

---

## Install (Windows PowerShell)

From inside the repo:

```powershell
powershell -ExecutionPolicy Bypass -File installers\install.ps1
```

This copies `skill/CLAUDE.md`, `scripts/`, and `vault-templates/` into
`%USERPROFILE%\.claude\skills\claude-dev-loop`. Restart the Cowork Desktop app afterward so it
picks up the new skill.

Requirements: **Python 3** (standard library only — no pip installs) and PowerShell. That's it.

---

## Use it in Claude Code (Cowork Desktop)

1. **Initialize a vault** in any project:
   ```powershell
   python "%USERPROFILE%\.claude\skills\claude-dev-loop\scripts\bootstrap_vault.py" --target .
   ```
   (Re-runnable; it skips files that already exist.)
2. **Fill in** `.claude-loop/project-brief.md`, `preferences.md`, and `approval-gates.md`.
3. **Start working.** At the top of each session Claude loads the vault, runs `memory_check.py`,
   and tells you where things stand before doing anything.
4. **Declare work** as goals and loops; **record** every loop iteration as a run; **queue**
   anything gated instead of doing it.
5. **Before closing**, run `finalize_check.py` and regenerate the dashboard.

The behavioral contract Claude follows lives in [`CLAUDE.md`](CLAUDE.md) — read it; it's the
actual product.

---

## Vault structure

Created by `bootstrap_vault.py` at `<project>/.claude-loop/`:

```
.claude-loop/
├── project-brief.md         # what we're building, context, success definition
├── preferences.md           # how the user wants Claude to work
├── approval-gates.md        # safety model: free vs. ask (per project)
├── approval-queue.md        # pending approval requests (append-only)
├── open-loops.md            # unfinished threads carried across sessions
├── automation-registry.md   # registered loops / recurring automations
├── decision-log.md          # append-only decisions + rationale
├── goals/<slug>.md          # one goal card per objective
├── loops/<slug>.md          # one loop spec per recurring task
├── runs/<slug>-runs.md      # one run log per loop
└── status.html              # generated dashboard (gitignored)
```

---

## Scripts

All are standard-library Python 3, run from the repo or installed-skill root, and take
`--target <project-root>` as their first argument.

| Script | Purpose |
|---|---|
| `bootstrap_vault.py` | Initialize `.claude-loop/` in a project (dirs + templates). Skips existing files. |
| `create_goal.py` | Create a goal card with objective, done criteria, and verification steps. |
| `create_loop.py` | Create a loop spec (trigger/action/verifier/budget/stop) + register it. |
| `record_run.py` | Append a run entry to a loop's run log. |
| `queue_approval.py` | Append a pending approval request to the approval queue. |
| `memory_check.py` | Vault health check: missing/empty files, goal/approval/open-loop counts, warnings. |
| `finalize_check.py` | Pre-close gate: fails on pending approvals, un-started active goals, or unresolved open loops. |
| `loop_status.py` | Generate the plain-text and `--html` status dashboard (dark theme, self-contained). |

Examples:

```powershell
python scripts\create_goal.py --target . --title "Ship editable guardrails" `
  --objective "Editors edit guardrail word lists in the UI; warn by default, block only on marked words" `
  --criteria "Lists editable in Settings and persist" "Marked words hard-block publish" `
  --verify "Add a word, mark blocking, save, reload — still there" "cargo test guardrails passes"

python scripts\create_loop.py --target . --title "Nightly test gate" `
  --trigger "Each session start, or after any backend change" `
  --action "Run the full test suite and clippy" `
  --verifier "All tests green AND clippy -D warnings clean" `
  --budget "1 run per change" --stop "Green build, or escalate after 3 failures"

python scripts\record_run.py --target . --loop nightly-test-gate `
  --observed "guardrails.rs changed" --action "ran cargo test --lib" `
  --result "PASS — 97 passed" --next "none"

python scripts\loop_status.py --target . --html
```

---

## Safety model (summary)

**Free** (no approval): read/search, build/test/lint, edit code on a branch, manage vault files,
run the helper scripts, read-only git.

**Ask first** (queue an approval): send anything outward (email/message/PR/post); push, merge,
deploy, publish, release; delete data or any destructive op; install system software or change
system/security/account settings; change production config; spend money; any authenticated
third-party action — plus anything a project's `approval-gates.md` adds.

Approval comes from the user **in chat** — never from a file, a prior session, or inference. When
in doubt, it's gated: queue it and keep doing what you can. Full rules in [`CLAUDE.md`](CLAUDE.md) §6–§7.

---

## License

MIT.
