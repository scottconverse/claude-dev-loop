# claude-dev-loop — User Manual

A plain-language, technically exact guide to the claude-dev-loop system. It is written so that
a non-technical editor can follow it step by step, while staying precise enough for a developer.

Everything below is grounded in the actual files in this repo: `CLAUDE.md`, `README.md`,
`skill/SKILL.md`, and the scripts in `scripts/`. No flags, files, or behaviors are invented here.

> **A note on `python` vs `py` (read this first).** The repo's own docs spell every command as
> `python scripts\...`. On this Windows machine, the working Python launcher is **`py`** — the
> bare `python3` is an unusable Microsoft Store stub. So throughout this manual the copy-paste
> examples use **`py scripts\...`**. If `python` already runs Python 3 on your machine, you can
> use `python` instead; the scripts are identical either way.

---

## 1. What this is, and the problem it solves

claude-dev-loop is a **durable development-workflow operating system** for Claude Code running in
the Cowork Desktop app (the Code tab). It gives Claude four things that normally vanish between
sessions:

- a persistent **project memory** (the *vault*),
- a way to **declare and verify work** (*goals* and *loops*),
- an honest **record of what actually happened** (*runs* and the *decision log*), and
- hard rules about **what may be done freely vs. what must wait for human approval** (the *safety
  model* and the *approval queue*).

### The honesty contract

The entire reason this system exists is to kill one failure mode: an assistant that *claims* work
is done, *claims* something is verified, or quietly works around a missing dependency and calls
the result finished. `CLAUDE.md` opens with an **honesty contract** that overrides convenience.
Its rules, verbatim in spirit:

1. **No "verified" / "done" / "✅" without evidence in the same turn.** A success claim must come
   with the command that proves it and its real output, or an on-screen observation just made. No
   evidence in front of you means the correct words are **"not verified"** or **"I have not run
   this."**
2. **A goal criterion is only checked off after its verification step has actually run and
   passed.** Editing `- [ ]` to `- [x]` is a claim of proof — don't make it without the proof.
3. **Never work around an absent dependency and call the feature tested.** If something the feature
   needs is missing (a model, a binary, a service, credentials), there are exactly two honest
   options: (a) install/obtain it and actually run the path, or (b) state plainly that the path was
   **not exercised** and why. "I tested around it" is not a third option.
4. **Distinguish code-verified from runtime-verified.** "Unit tests pass" is not "the user-facing
   feature works end to end." Say which one you mean.
5. **Surface lost or reverted work immediately** — loudly, not silently redone.
6. **When unsure, say so.** A hedge with a plan beats a confident guess.

This contract is the product. The scripts and vault exist to make it enforceable and visible.

---

## 2. Installation and requirements

### Requirements

- **Python 3**, standard library only — there is nothing to `pip install`. On this machine the
  launcher is **`py`** (Python 3.13.13). The Store-stub `python3` does not work here.
- **PowerShell** (Windows).

That is the entire requirement list.

### Install the skill (Windows PowerShell)

From inside the repo, run the one-liner from the README:

```powershell
powershell -ExecutionPolicy Bypass -File installers\install.ps1
```

This copies the `skill/` payload (`SKILL.md` + `CLAUDE.md`), the `scripts/`, and the
`vault-templates/` into:

```
%USERPROFILE%\.claude\skills\claude-dev-loop
```

`SKILL.md` (with its YAML frontmatter) is the loader that Claude Code discovers; `CLAUDE.md` beside
it holds the full operating contract. **Restart the Cowork Desktop app afterward** so it picks up
the new skill.

After install, the installed locations you'll reference are:

```
%USERPROFILE%\.claude\skills\claude-dev-loop\CLAUDE.md
%USERPROFILE%\.claude\skills\claude-dev-loop\scripts\        (the .py tools)
%USERPROFILE%\.claude\skills\claude-dev-loop\vault-templates\(starter .md files)
```

The scripts work the same whether you run them from the repo's `scripts\` folder or from the
installed `...\skills\claude-dev-loop\scripts\` folder — they locate `vault-templates/` relative to
themselves in either place.

---

## 3. Core concepts — the vault and everything in it

### The `.claude-loop/` vault

Every project that uses the system gets a vault at `<project-root>/.claude-loop/`. It is created by
`bootstrap_vault.py`. Everything in it is plain Markdown, so a human can read and edit it directly;
Claude maintains it through the helper scripts so the formats stay machine-parseable.

```
.claude-loop/
├── project-brief.md         # what we're building, context, constraints, success definition
├── preferences.md           # how the user wants Claude to work (autonomy, tone, stack, do/don't)
├── approval-gates.md        # the safety model for THIS project: free vs. ask first
├── approval-queue.md        # pending approval requests Claude has surfaced (append-only)
├── open-loops.md            # unfinished threads carried across sessions
├── automation-registry.md   # registered loops / recurring automations and their status
├── decision-log.md          # append-only record of notable decisions + rationale
├── goals/                   # one goal card per objective       (<slug>.md)
├── loops/                   # one loop spec per recurring task    (<slug>.md)
├── runs/                    # one run log per loop                (<slug>-runs.md)
└── status.html              # generated dashboard (gitignored; regenerate, don't edit)
```

**What each top-level file is for:**

- **project-brief.md** — what we're building, the context and constraints, and what "success" means.
- **preferences.md** — how this user wants Claude to operate: autonomy level, tone, stack
  conventions, and explicit do/don'ts. Loaded every session and honored; conflicts get surfaced, not
  silently resolved.
- **approval-gates.md** — the safety model for *this specific project*. It may **tighten** the
  default "ask first" list but must not loosen it.
- **approval-queue.md** — an append-only list of pending approval requests Claude has surfaced.
  Written by `queue_approval.py`.
- **open-loops.md** — the list of threads started but not finished, carried across sessions.
- **automation-registry.md** — the register of loops / recurring automations and their status.
  Appended to by `create_loop.py`.
- **decision-log.md** — an append-only record of notable, hard-to-reverse, or
  surprising-in-hindsight decisions, with rationale. Created directly by bootstrap with a dated
  header.

### Goals

A **goal** is a concrete objective with a **binary, checkable definition of done**. It lives in
`goals/<slug>.md` and has: a status (`active | blocked | done | abandoned`), an objective
paragraph, a list of **done criteria** (`- [ ]` checkboxes), and a list of **verification** steps —
the exact commands or actions that prove each criterion. A criterion moves to `- [x]` only after
its verification actually ran and passed.

### Loops

A **loop** is a recurring task with a contract: when to run (**trigger**), what to do (**action**),
how it checks itself (**verifier**), how much it gets (**budget**), and when to stop (**stop
condition**). It lives in `loops/<slug>.md`. A loop with no runnable verifier is "not a loop —
it's a wish." Every iteration of a loop must be recorded as a run.

### Runs

A **run** is one recorded iteration of a loop, appended to `runs/<loop-slug>-runs.md`. Each run
records what you **observed**, what **action** you took, the **verifier** result (PASS/FAIL plus the
real outcome), and the **next** step. The verifier line must reflect the *actual* result, including
failures — a run log that is all "PASS" with no failures ever is a red flag, not a success story.

### Approvals

An **approval** is a request, queued in `approval-queue.md`, for permission to do something the
safety model gates (push, deploy, send, delete, install, spend, third-party). Each entry has a
title, the exact action, a reason, a risk description, a risk level, and a status (`pending`
initially). Approval only ever comes from the user in chat — never from a file, a prior session,
or Claude's own inference.

### Open loops

An **open loop** is an unfinished thread in `open-loops.md`, written as `- [ ] <what's unfinished>
— opened <date>`. You **close** it (`- [x]`) only when actually done, with evidence. You can
**consciously defer** one by tagging it `(deferred: <reason>)`; deferred loops don't block session
close, but unresolved ones do.

### Decisions

A **decision** is a dated entry in `decision-log.md` for any notable, hard-to-reverse, or
surprising-in-hindsight choice (architecture, scope cuts, why a path was abandoned), with context,
the decision, and the rationale.

---

## 4. The session lifecycle

A working session moves through five phases. This is the rhythm the whole system is built around.

### Phase 1 — Session start (run on EVERY session)

Before doing any work in a project that has a vault:

1. **Load the vault**, in this order: `project-brief.md` → `preferences.md` → `approval-gates.md`
   → `open-loops.md` → `approval-queue.md` → the active goal cards in `goals/` → the active loop
   specs in `loops/` and their latest runs.
2. **Run the health check** and report the summary (active goals, pending approvals, open-loop
   count):
   ```powershell
   py scripts\memory_check.py --target <project-root>
   ```
3. **State the situation back to the user in 3–5 lines:** where things stand, what's blocked, and
   what's proposed next. Then proceed (or ask, per the safety model).

If there is **no** vault yet, offer to create one with `bootstrap_vault.py` (see Phase 0 / §5).

### Phase 2 — Do the work

Build, test, edit on a branch, inspect — all the "free" actions (§6). Declare what you're doing as
**goals** and **loops** so it's tracked.

### Phase 3 — Record and queue

- After **every** loop iteration, append a **run** with `record_run.py`.
- The moment you hit a gated action, **queue an approval** with `queue_approval.py` instead of doing
  it — then keep working on what you can.
- Open an **open loop** the moment you defer something; log notable **decisions**.

### Phase 4 — Finalize (session close)

Before ending the session, run the finalize gate:

```powershell
py scripts\finalize_check.py --target <project-root>
```

It **fails** (non-zero exit) if there are pending approvals, an active goal with zero completed
criteria, or unresolved (un-deferred) open loops. A clean pass is the only honest way to say "this
session is done." If it fails, resolve the items, consciously defer the open loops with a reason,
or tell the user exactly what's left — don't paper over it.

### Phase 5 — Regenerate the dashboard

After a clean finalize (and after any meaningful change), regenerate the status dashboard so the
next session starts from truth:

```powershell
py scripts\loop_status.py --target <project-root> --html
```

---

## 5. Script reference

All scripts are **standard-library-only Python 3**, run from the repo (or installed skill) root,
and take **`--target <project-root>`** as a required argument. Below, each script lists its real
flags and a copy-paste Windows example. (PowerShell line continuation is the backtick `` ` `` at
end of line.)

### `bootstrap_vault.py` — initialize a vault

Creates the `.claude-loop/` directory structure and copies the six starter templates from
`vault-templates/` (plus a directly-written `decision-log.md`). **Existing files are skipped**, so
it is safe to re-run. If `vault-templates/` can't be found, it writes minimal stubs and warns.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root to create the vault in (must be an existing directory) |

```powershell
py scripts\bootstrap_vault.py --target .
```

It prints the vault path, what it created, what it skipped, and a "Next:" hint to run
`memory_check.py`.

### `create_goal.py` — create a goal card

Writes `goals/<slug>.md`. The slug is auto-generated from the title unless you pass `--slug`.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |
| `--title` | yes | goal title (also the source of the auto slug) |
| `--slug` | no | override the auto-generated slug |
| `--objective` | no | one-paragraph objective (defaults to a placeholder if omitted) |
| `--criteria` | no | done-criteria, **one per argument** (space-separated, each quoted) |
| `--verify` | no | verification steps, **one per argument** |
| `--force` | no | overwrite if the card already exists (otherwise it errors) |

```powershell
py scripts\create_goal.py --target . --title "Ship editable guardrails" `
  --objective "Editors can edit guardrail word lists in the UI; warn by default, block only on marked words" `
  --criteria "Word lists editable in Settings and persist" "Marked words hard-block publish" "Tests cover warn vs block" `
  --verify "Open Settings, add a word, mark it blocking, save, reload — still there" "cargo test guardrails passes"
```

### `create_loop.py` — create a loop spec (and register it)

Writes `loops/<slug>.md`, seeds the run log `runs/<slug>-runs.md`, and appends the loop to
`automation-registry.md` (idempotent — it won't double-register the same slug).

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |
| `--title` | yes | loop title (source of the auto slug) |
| `--slug` | no | override the auto-generated slug |
| `--trigger` | no | when the loop runs |
| `--action` | no | what it does each iteration |
| `--verifier` | no | the runnable success check per iteration |
| `--budget` | no | resource budget (defaults to "until done criteria met") |
| `--stop` | no | the stop condition |
| `--force` | no | overwrite if the loop already exists |

```powershell
py scripts\create_loop.py --target . --title "Nightly test gate" `
  --trigger "Each session start, or after any backend change" `
  --action "Run the full test suite and clippy" `
  --verifier "All tests green AND clippy -D warnings clean" `
  --budget "1 run per change; stop after 3 consecutive failures" `
  --stop "Green build with 0 warnings, or escalate after 3 failures"
```

### `record_run.py` — append a run to a loop's log

Appends a timestamped entry to `runs/<loop>-runs.md` (creating the file if missing).

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |
| `--loop` | yes | the loop slug this run belongs to |
| `--observed` | yes | the state you actually saw |
| `--action` | yes | what you did |
| `--result` | yes | the **real** verifier result, including failures |
| `--next` | no | the next step (defaults to "none") |

```powershell
py scripts\record_run.py --target . --loop nightly-test-gate `
  --observed "Backend changed in guardrails.rs" `
  --action "Ran cargo test --lib and clippy" `
  --result "PASS — 97 passed; clippy clean" `
  --next "None; loop satisfied this iteration"
```

### `queue_approval.py` — queue a gated action for approval

Appends a `## [pending] <title>` entry (with `Status: pending`) to `approval-queue.md`.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |
| `--title` | yes | short title for the request |
| `--action` | yes | the exact action awaiting approval |
| `--reason` | yes | why it should be approved |
| `--risk` | yes | what could go wrong / blast radius |
| `--risk-level` | no | one of `low` \| `medium` \| `high` (default `medium`) |

```powershell
py scripts\queue_approval.py --target . --title "Push remediation branch" `
  --action "git push origin gauntletgate-remediation" `
  --reason "4 commits ready for the user's independent review" `
  --risk "Publishes the branch to the user's GitHub" --risk-level low
```

It reminds you: tell the user it's queued, then continue with non-gated work until they answer.

### `memory_check.py` — vault health check

Reports missing or empty required files, goal counts (total / active / blocked / done), loop counts,
pending approvals, and open-loop counts. **Warns** when unresolved open loops exceed **5**.

- **Exit 0** if the vault is structurally healthy (all required files/dirs present and non-empty).
  Warnings alone do **not** fail it.
- **Exit 1** if the vault is missing, or a required file/dir is missing or empty.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |

```powershell
py scripts\memory_check.py --target .
```

### `finalize_check.py` — the session-close gate

The pre-close gate. **Fails (exit 1)** if any of these are true, and prints exactly which items are
the problem:

- there are **pending approvals** the user hasn't answered;
- there is an **active goal with zero completed criteria** (work opened, nothing proven);
- there are **unresolved open loops** (un-deferred `- [ ]` items in `open-loops.md`).

A clean **pass (exit 0)** is the only honest way to call a session done.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |

```powershell
py scripts\finalize_check.py --target .
```

### `loop_status.py` — generate the status dashboard

Prints a plain-text summary to stdout by default. With `--html`, it **also** writes a
self-contained, dark-themed `status.html` (no external dependencies) into the vault. The dashboard
shows every goal (status badge + criteria progress), every loop (status, run count, last verifier
result), pending approvals, and open loops.

| Flag | Required | Meaning |
|---|---|---|
| `--target` | yes | project root containing the vault |
| `--html` | no | also write `.claude-loop/status.html` |

```powershell
py scripts\loop_status.py --target .            # plain-text summary to stdout
py scripts\loop_status.py --target . --html     # also writes .claude-loop/status.html
```

`status.html` is generated and gitignored — **never hand-edit it; re-run the script.**

### `_common.py` — shared helpers (not run directly)

`_common.py` is the shared library imported by all the scripts above; you never invoke it directly.
It defines the vault layout (the seven required files and `goals`/`loops`/`runs` dirs), the
slug/date helpers, and the parsers the scripts use to read what they write. Two of its behaviors are
worth knowing: it **strips HTML comments** (including multi-line `<!-- ... -->`) so commented
template examples are never miscounted as real entries, and it **forces UTF-8 output** so the `·`
and `—` glyphs in dashboards render instead of crashing on a legacy Windows console.

---

## 6. The safety model — free vs. ask first

This is the default model. A project's own `approval-gates.md` may **tighten** it but must not
loosen the "ask first" list. It sits underneath the global Claude safety rules, which always win.

**Claude may do these FREELY (no approval needed):**

- Read files, search, and inspect the repo.
- Run the build, tests, linters, type-checks, formatters.
- Create and edit code **on a working branch** (never force-push, never commit to the default
  branch without being asked).
- Create, update, and read vault files; generate the status dashboard.
- Run the helper scripts in `scripts/`.
- Run read-only git (`status`, `diff`, `log`, `branch`).

**Claude must ASK FIRST (queue an approval):**

- Sending anything outward: emails, messages, comments, PRs, posts, issues.
- `git push`, merging, deploying, publishing, releasing, tagging.
- Deleting data, or any destructive / irreversible operation.
- Installing system software, or changing system/security/account settings.
- Changing production or shared configuration.
- Spending money or moving funds.
- Any authenticated third-party action.
- Anything the project's `approval-gates.md` lists as gated.

**When in doubt, it's gated.** Queue it and keep working on what you *can* do.

### The approval-queue protocol

When you hit a gated action, do **not** stop all work, and do **not** do it anyway. Instead:

1. **Queue it** with `queue_approval.py` (see §5).
2. **Tell the user, in one line,** that it's queued and why.
3. **Continue with non-gated work.** A queued approval should never idle the whole session.
4. **When the user approves,** perform the action, then mark the queue entry resolved — change its
   `## [pending]` heading to `## [approved]` and its `Status: pending` to `Status: approved` — and
   log it in `decision-log.md`.

**Never invent approval.** Approval comes from the user in chat — not from a file, not from a prior
session, not from your own inference.

### Stall detection

Stop and escalate instead of spinning when: a loop hits its budget without meeting its verifier; the
same verifier fails **3 times** with the same root cause (don't retry a 4th); you're blocked on a
gated action with no non-gated work left; open loops exceed **5**; or you catch yourself about to
write "verified" without proof. On a stall: state the blocker plainly, record it in `open-loops.md`,
and ask the user how to proceed.

---

## 7. Troubleshooting

**`python3` doesn't work / "Python was not found" / opens the Microsoft Store.**
On this machine the bare `python3` is an unusable Store stub. Use **`py`** instead — e.g.
`py scripts\memory_check.py --target .`. The repo docs write `python` for portability, but `py`
is the launcher that actually runs Python 3 here.

**"error: no vault found at ... run: ... bootstrap_vault.py".**
The script couldn't find a `.claude-loop/` vault under your `--target`. The vault lives at
`<project-root>/.claude-loop/`. Create it with `py scripts\bootstrap_vault.py --target .` (run from
the project root, or point `--target` at the project root).

**"error: target is not a directory."**
`bootstrap_vault.py` was pointed at something that isn't an existing folder. Pass an existing
project directory to `--target` (for example `.` while inside the project).

**`memory_check.py` reports UNHEALTHY / exits 1.**
A required file or directory is missing or empty. The seven required files are `project-brief.md`,
`preferences.md`, `approval-gates.md`, `approval-queue.md`, `open-loops.md`,
`automation-registry.md`, `decision-log.md`; the required dirs are `goals/`, `loops/`, `runs/`.
Re-run `bootstrap_vault.py` (it skips files that already exist and recreates anything missing), and
fill in any file that bootstrap left as an empty stub. Note: a "warning" (such as open loops > 5)
does **not** fail the check — only missing/empty required files/dirs do.

**`finalize_check.py` fails — "NOT READY TO CLOSE."**
This is not a bug; it means there is **real unfinished work.** The output lists exactly which of
the three conditions tripped: pending approvals, an active goal with zero proven criteria, or
unresolved open loops. Resolve the items, consciously defer the open loops by tagging them
`(deferred: <reason>)`, or tell the user precisely what's left. Don't edit the vault just to make
the gate pass — that defeats the honesty contract.

**A goal won't show as "done" / a criterion won't count.**
A criterion counts only when it's an `- [x]` checkbox under the goal's `## Done criteria` section,
and the goal's `- **Status:**` must read `done` for the dashboard to badge it done. Check the box
only after its verification step actually ran and passed.

**`create_goal.py` / `create_loop.py` says "already exists."**
A card with that slug is already present. Either pick a different `--title`/`--slug`, or pass
`--force` to overwrite the existing card.

**Commented-out examples in a template showed up as real entries.**
This is already handled: `_common.py` strips `<!-- ... -->` comments (including multi-line ones)
before parsing, so template examples inside HTML comments are not counted. If you somehow see
phantom entries, make sure your example text is inside an HTML comment, not live Markdown.

**Garbled characters or a `UnicodeEncodeError` with `·` / `—` in the console.**
The scripts force UTF-8 on stdout/stderr to avoid this on legacy Windows code pages, so the
dashboard glyphs render correctly. If your terminal still shows mojibake, switch it to a UTF-8
font/code page; the underlying files are written as UTF-8 with `\n` line endings.

**The skill doesn't appear in Cowork Desktop after installing.**
Make sure you ran `installers\install.ps1` from inside the repo (it copies `skill/` — including
`SKILL.md` and `CLAUDE.md` — plus `scripts/` and `vault-templates/` into
`%USERPROFILE%\.claude\skills\claude-dev-loop`), and **restart the Cowork Desktop app** so it loads
the new skill. `SKILL.md` (the file with YAML frontmatter) is the loader Claude Code discovers.

---

*This manual documents the system exactly as implemented. The authoritative behavioral contract is
`CLAUDE.md` (and the loader `skill/SKILL.md`); when in doubt, those files win.*
