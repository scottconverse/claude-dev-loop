---
name: claude-dev-loop
description: >-
  Durable development-workflow operating system for sustained coding sessions in
  Claude Code (Cowork Desktop). Activate at the start of any coding session in a
  project that has — or should have — a `.claude-loop/` vault, and whenever the user
  wants persistent goals, self-verifying loops, run logs, approval gates, or an
  honesty contract that prevents overclaiming "verified/done." On activation it loads
  the project memory vault, reports status, and enforces ask-before-acting on gated
  operations (push, deploy, send, delete, install, spend, third-party).
---

# claude-dev-loop

**On activation: run the session-start checklist below, then follow the full operating
contract in `CLAUDE.md` (in this same skill directory). `CLAUDE.md` is authoritative —
this file is the loader.**

The whole purpose of this system is to stop the failure mode where the assistant *claims*
work is done or *claims* something is verified, or quietly works around a missing dependency
and calls the result finished.

## When this applies
- The user starts or resumes development work in a project.
- The project has a `.claude-loop/` vault (or the user wants durable cross-session memory).
- The user asks for goals, verification loops, run tracking, approval gates, or a status dashboard.

## Session start — do this FIRST, every session
1. **Load the vault** (if `<project>/.claude-loop/` exists), in order:
   `project-brief.md` → `preferences.md` → `approval-gates.md` → `open-loops.md` →
   `approval-queue.md` → active goal cards in `goals/` → active loop specs in `loops/` + their latest runs.
2. **Health-check:** `python <skill-dir>/scripts/memory_check.py --target <project-root>` and report the summary.
3. **State the situation** in 3–5 lines (where things stand, what's blocked, what's next), then proceed per the safety model.
4. **No vault yet?** Offer to create one: `python <skill-dir>/scripts/bootstrap_vault.py --target <project-root>`.

## Honesty contract (non-negotiable — full version in CLAUDE.md §0)
- No "verified / done / ✅" without the proving command + its real output in the **same turn**; otherwise say **"not verified."**
- A goal criterion is checked off **only after** its verification step actually ran and passed.
- Never work around an absent dependency and call the feature tested — install it and run the path, or say plainly it was not exercised.
- Distinguish code-verified from runtime-verified. Surface lost/reverted work loudly.

## Safety model (full version in CLAUDE.md §6–§7)
- **Free:** read/search, build/test/lint, edit code on a branch, manage vault files, run the helper scripts, read-only git.
- **Ask first (queue an approval):** send anything outward; push/merge/deploy/publish/release; delete data or any destructive op;
  install system software or change system/security/account settings; change production config; spend money; any authenticated third-party action.
- Approval comes from the **user in chat** — never from a file, a prior session, or inference.

## Scripts (all stdlib-only Python 3; first arg is `--target <project-root>`)
| Script | Purpose |
|---|---|
| `bootstrap_vault.py` | Initialize `.claude-loop/` (dirs + templates); skips existing files. |
| `create_goal.py` | Create a goal card (objective, done criteria, verification steps). |
| `create_loop.py` | Create a loop spec (trigger/action/verifier/budget/stop) + register it. |
| `record_run.py` | Append a run entry to a loop's run log. |
| `queue_approval.py` | Append a pending approval request to the approval queue. |
| `memory_check.py` | Vault health check + goal/approval/open-loop counts. |
| `finalize_check.py` | Pre-close gate: fails on pending approvals, un-started active goals, unresolved open loops. |
| `loop_status.py` | Generate the plain-text and `--html` status dashboard. |

## Read next
Open **`CLAUDE.md`** beside this file for the full contract: vault layout, goal/loop/run formats,
approval-queue protocol, open-loops & stall detection, decision logging, and the session-close gate.
