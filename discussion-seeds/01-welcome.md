# Welcome to claude-dev-loop

Hi, and thanks for stopping by. This is the home base for **claude-dev-loop** — a durable development-workflow operating system for Claude Code running in the Cowork Desktop app (Code tab). If you do sustained coding sessions and you're tired of an assistant that *says* "done" without proof, you're in the right place.

## What this actually is

claude-dev-loop gives Claude four things it normally lacks across a long project:

- **A persistent project memory** — the **vault**, a `.claude-loop/` directory of plain Markdown files that survives across sessions.
- **A way to declare and verify work** — **goals** (a binary, checkable definition of done) and **loops** (a recurring task with a runnable verifier).
- **An honest record of what happened** — **run logs** and an append-only **decision log**.
- **Hard rules about what's safe to do freely vs. what must wait for you** — the **safety model** and the **approval queue**.

It's modeled on `scottconverse/codex-dev-loop`, rebuilt native to Claude Code instead of OpenAI Codex.

## The honesty contract (the whole reason this exists)

The system exists to kill one specific failure mode: an assistant that *claims* work is done, *claims* something is verified, or quietly works around a missing dependency and calls the result finished. `CLAUDE.md` opens with an honesty contract that makes "verified" mean *proven in the same turn, with evidence* — and if there's no evidence, the correct words are **"not verified"** or **"I have not run this."**

A few of its rules, so you know the flavor:

- No "verified / done / ✅" without the proving command and its real output in the same turn.
- A goal criterion is checked off (`- [ ]` → `- [x]`) **only after** its verification step actually ran and passed.
- Never work around an absent dependency and call the feature tested — install it and run the path, or say plainly it was not exercised.
- Distinguish code-verified ("unit tests pass") from runtime-verified ("the feature works end to end").

There's a whole discussion dedicated to this — see **The honesty contract** thread.

## Install (Windows PowerShell)

From inside the repo:

```powershell
powershell -ExecutionPolicy Bypass -File installers\install.ps1
```

This copies the `skill/` payload (`SKILL.md` + `CLAUDE.md`), `scripts/`, and `vault-templates/` into `%USERPROFILE%\.claude\skills\claude-dev-loop`. `SKILL.md` (with YAML frontmatter) is the loader Claude Code discovers; `CLAUDE.md` beside it holds the full operating contract. **Restart the Cowork Desktop app afterward** so it picks up the new skill.

Requirements are deliberately tiny: **Python 3** (standard library only — no pip installs) and PowerShell. That's it.

## Bootstrap your first vault

In any project you want durable memory for:

```powershell
py "%USERPROFILE%\.claude\skills\claude-dev-loop\scripts\bootstrap_vault.py" --target .
```

`bootstrap_vault.py` creates `<project>/.claude-loop/` with the `goals/`, `loops/`, and `runs/` subdirectories plus the seven top-level files: `project-brief.md`, `preferences.md`, `approval-gates.md`, `approval-queue.md`, `open-loops.md`, `automation-registry.md`, and `decision-log.md`. It's re-runnable — it **skips any file that already exists**, so you can run it again without clobbering your edits.

(On Windows the documented examples use `python`, but the Python launcher is `py`. If `python` isn't on your PATH, use `py` — both invoke the same standard-library scripts.)

After bootstrapping:

1. **Fill in** `project-brief.md` (what you're building and why), `preferences.md` (how you want Claude to work), and `approval-gates.md` (your project's safety model).
2. **Start working.** At the top of every session Claude loads the vault, runs `memory_check.py`, and tells you where things stand before doing anything.
3. **Declare work** as goals and loops; **record** every loop iteration as a run; **queue** anything gated instead of just doing it.
4. **Before closing**, run `finalize_check.py` and regenerate the dashboard with `loop_status.py --html`.

## Say hi

Drop a comment below: what are you building, and what's the failure mode you most want to stop? If you've got a vault running already, the **Show and tell** thread is the place to share it.

Glad you're here.
