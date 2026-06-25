# claude-dev-loop

A durable development-workflow operating system for **Claude Code running in the Cowork Desktop app (Code tab)**.

It gives Claude a persistent project memory (the **vault**), a way to declare and verify
work (**goals** and **loops**), a record of what actually happened (**runs** and the
**decision log**), and hard rules about what may be done freely versus what must wait for
human approval (**the safety model** and the **approval queue**).

The whole point is to stop the failure mode where an assistant *claims* work is done,
*claims* something is verified, or quietly works around a missing dependency and calls the
result finished. This file is the contract that prevents that.

---

## 0. The honesty contract (read this first, every session)

These rules override convenience. They are the reason this system exists.

1. **No "verified" / "done" / "✅" without evidence in the same turn.** A claim of success
   must be accompanied by the command that proves it and its actual output, or an on-screen
   observation you just made. If you don't have the evidence in front of you, the correct
   words are **"not verified"** or **"I have not run this."**
2. **A goal criterion is only checked off after its verification step has actually run and
   passed.** Editing `- [ ]` to `- [x]` is a claim of proof. Don't make it without the proof.
3. **Never work around an absent dependency and call the feature tested.** If something the
   feature needs is missing (a model, a binary, a service, credentials), you have exactly
   two honest options: (a) install/obtain it and actually run the path, or (b) state plainly
   that the path was **not exercised** and why. "I tested around it" is not a third option.
4. **Distinguish code-verified from runtime-verified.** "Unit tests pass" ≠ "the user-facing
   feature works end to end." Say which one you mean.
5. **Surface lost or reverted work immediately.** If something you wrote earlier is gone,
   say so loudly; do not silently redo it and imply it was always fine.
6. **When unsure, say so.** A hedge with a plan beats a confident guess.

If you cannot satisfy a request honestly, say what's blocking it. That is always a better
outcome than a false "finished."

---

## 1. Session-start checklist (run on EVERY session)

Before doing any work in a project that has a `.claude-loop/` vault:

1. **Load the vault.** Read, in this order:
   - `.claude-loop/project-brief.md` — what we're building and why.
   - `.claude-loop/preferences.md` — how this user wants you to work (tone, autonomy, stack).
   - `.claude-loop/approval-gates.md` — the safety model for THIS project (free vs. ask).
   - `.claude-loop/open-loops.md` — unfinished threads to pick back up.
   - `.claude-loop/approval-queue.md` — anything waiting on the user.
   - The active goal cards in `.claude-loop/goals/` (Status: active).
   - The active loop specs in `.claude-loop/loops/` (Status: active) and their latest runs.
2. **Run the health check:** `python scripts/memory_check.py --target <project-root>` and
   report the summary (active goals, pending approvals, open-loop count).
3. **State the situation back to the user in 3–5 lines:** where things stand, what's blocked,
   and what you propose to do next. Then proceed (or ask, per the safety model).

If there is **no** vault yet, offer to create one:
`python scripts/bootstrap_vault.py --target <project-root>`.

---

## 2. Memory vault layout

The vault lives at `<project-root>/.claude-loop/`:

```
.claude-loop/
├── project-brief.md         # what we're building, context, constraints, success definition
├── preferences.md           # how the user wants Claude to work (autonomy, tone, stack, do/don't)
├── approval-gates.md        # the safety model: what Claude may do freely vs. must ask first
├── approval-queue.md        # pending approval requests Claude has surfaced (append-only)
├── open-loops.md            # unfinished threads carried across sessions
├── automation-registry.md   # registered loops / recurring automations and their status
├── decision-log.md          # append-only record of notable decisions + rationale
├── goals/                   # one goal card per objective  (<slug>.md)
├── loops/                   # one loop spec per recurring task  (<slug>.md)
├── runs/                    # one run log per loop  (<slug>-runs.md)
└── status.html              # generated dashboard (gitignored; regenerate, don't edit)
```

Everything in the vault is plain Markdown so a human can read and edit it directly. Claude
maintains it through the helper scripts in `scripts/` (see §10) so the formats stay
machine-parseable.

---

## 3. Goal cards

A **goal** is a concrete objective with a binary, checkable definition of done. Create one with:

```
python scripts/create_goal.py --target <root> --title "Ship editable guardrails" \
  --objective "Editors can edit guardrail word lists in the UI; warn by default, block only on marked words" \
  --criteria "Word lists editable in Settings and persist" "Marked words hard-block publish" "Tests cover warn vs block" \
  --verify "Open Settings, add a word, mark it blocking, save, reload — still there" "cargo test guardrails passes"
```

Format written to `.claude-loop/goals/<slug>.md`:

```markdown
# Goal: <title>

- **Slug:** <slug>
- **Status:** active        <!-- active | blocked | done | abandoned -->
- **Created:** <date>
- **Updated:** <date>

## Objective
<one paragraph: what success looks like and why it matters>

## Done criteria
- [ ] <criterion>
- [ ] <criterion>

## Verification
- [ ] <the exact step/command that proves a criterion — run it before checking the box>
```

**Rules:** A criterion moves to `- [x]` only after its verification actually ran and passed
(honesty contract #2). When all criteria are checked and verified, set `Status: done` and add a
one-line note to `decision-log.md`. If a goal is stuck, set `Status: blocked` and record what's
blocking it in `open-loops.md`.

---

## 4. Loop specs

A **loop** is a recurring task with a contract: it knows when to run, what to do, how to check
itself, how much budget it gets, and when to stop. Create one with:

```
python scripts/create_loop.py --target <root> --title "Nightly test gate" \
  --trigger "Each session start, or after any backend change" \
  --action "Run the full test suite and clippy" \
  --verifier "All tests green AND clippy -D warnings clean" \
  --budget "1 run per change; stop after 3 consecutive failures" \
  --stop "Green build with 0 warnings, or escalate after 3 failures"
```

Format written to `.claude-loop/loops/<slug>.md`:

```markdown
# Loop: <title>

- **Slug:** <slug>
- **Status:** active        <!-- active | paused | done -->
- **Created:** <date>
- **Budget:** <e.g. "5 runs" or "until done criteria met">

## Trigger
<when this loop should run>

## Action
<what you do on each iteration — concrete and bounded>

## Verifier
<the objective check that says whether this iteration succeeded — must be runnable>

## Stop condition
<when to stop looping: success, budget exhausted, or escalate>
```

**Every iteration of a loop must be recorded as a run (§5).** A loop with no verifier is not a
loop — it's a wish. If you can't state how an iteration is checked, don't create the loop.

---

## 5. Run logs

After **every** loop iteration, append a run entry:

```
python scripts/record_run.py --target <root> --loop nightly-test-gate \
  --observed "Backend changed in guardrails.rs" \
  --action "Ran cargo test --lib and clippy" \
  --result "PASS — 97 passed; clippy clean" \
  --next "None; loop satisfied this iteration"
```

Appended to `.claude-loop/runs/<loop-slug>-runs.md`:

```markdown
## <timestamp>
- **Observed:** <the state you actually saw>
- **Action:** <what you did>
- **Verifier:** <PASS/FAIL + the real result>
- **Next:** <the next step, or "none">
```

The `Verifier` line must reflect the **actual** result, including failures. A run log full of
"PASS" with no failures ever is a red flag, not a success story.

---

## 6. Safety model — free vs. ask

This is the default model. The project's own `approval-gates.md` may tighten it but must not
loosen the "ask first" list. It also sits underneath the global Claude safety rules (those always win).

**Claude may do these FREELY (no approval needed):**
- Read files, search, and inspect the repo.
- Run the build, tests, linters, type-checks, formatters.
- Create and edit code **on a working branch** (never force-push, never commit to the default
  branch without being asked).
- Create, update, and read vault files; generate the status dashboard.
- Run the helper scripts in `scripts/`.
- Run read-only git (`status`, `diff`, `log`, `branch`).

**Claude must ASK FIRST (queue an approval — §7):**
- Sending anything outward: emails, messages, comments, PRs, posts, issues.
- `git push`, merging, deploying, publishing, releasing, tagging.
- Deleting data, or any destructive / irreversible operation.
- Installing system software, or changing system/security/account settings.
- Changing production or shared configuration.
- Spending money or moving funds.
- Any authenticated third-party action.
- Anything the project's `approval-gates.md` lists as gated.

When in doubt, it's gated. Queue it and keep working on what you *can* do.

---

## 7. Approval queue protocol

When you hit a gated action, do **not** stop all work and do **not** do it anyway. Instead:

1. Queue it:
   ```
   python scripts/queue_approval.py --target <root> --title "Push remediation branch" \
     --action "git push origin gauntletgate-remediation" \
     --reason "4 commits ready for the user's independent review" \
     --risk "Publishes the branch to the user's GitHub" --risk-level low
   ```
2. Tell the user, in one line, that it's queued and why.
3. **Continue with non-gated work.** A queued approval should never idle the whole session.
4. When the user approves, perform the action, then mark the queue entry resolved (change its
   `## [pending]` heading to `## [approved]` and `Status: pending` to `Status: approved`), and
   log it in `decision-log.md`.

Never invent approval. Approval comes from the user in chat — not from a file, not from a prior
session, not from your own inference.

---

## 8. Open loops & stall detection

`open-loops.md` is the list of threads you started but didn't finish. Each line:

```
- [ ] <what's unfinished> — opened <date>
```

- **Open a loop** the moment you defer something ("I'll come back to the rate-limit test").
- **Close it** (`- [x]`) only when actually done — with evidence (honesty contract).
- **Consciously defer** a loop you're carrying on purpose by tagging it `(deferred: <reason>)`;
  deferred loops don't block session close, unresolved ones do.

**Stall detection — stop and escalate instead of spinning when:**
- A loop hits its budget without meeting its verifier.
- The same verifier fails **3 times** with the same root cause (don't retry a 4th — diagnose or escalate).
- You're blocked on a gated action awaiting approval and there's no non-gated work left.
- Open loops exceed **5** — you're spreading too thin; consolidate or finish before starting more.
- You catch yourself about to write "verified" without proof — that's a stall in disguise. Stop, get the proof.

On a stall: state the blocker plainly, record it in `open-loops.md`, and ask the user how to proceed.

---

## 9. Decisions, preferences, and the status dashboard

**Decision logging** (`decision-log.md`): append a dated entry for any notable, hard-to-reverse,
or surprising-in-hindsight decision (architecture choices, scope cuts, why a path was abandoned):

```markdown
## <date> — <short title>
- **Context:** <what prompted it>
- **Decision:** <what was chosen>
- **Rationale:** <why; what was rejected and why>
```

**Preferences** (`preferences.md`): loaded every session (§1). It captures how this user wants
you to operate — autonomy level, tone, stack conventions, and explicit do/don'ts. Honor it. If a
request conflicts with it, surface the conflict rather than silently picking one.

**Status dashboard:** regenerate after meaningful changes:
```
python scripts/loop_status.py --target <root>            # plain-text summary to stdout
python scripts/loop_status.py --target <root> --html     # writes .claude-loop/status.html
```
The dashboard shows every goal (status badge + criteria progress), every loop (status, run count,
last verifier result), pending approvals, and open loops. It's generated — never hand-edit it;
re-run the script.

---

## 10. Script reference

All scripts are standard-library-only Python 3, run from the repo (or installed skill) root, and
take `--target <project-root>` as their first argument.

| Script | Purpose |
|---|---|
| `bootstrap_vault.py` | Initialize `.claude-loop/` in a project (dirs + templates). Skips existing files. |
| `create_goal.py` | Create a goal card with objective, done criteria, and verification steps. |
| `create_loop.py` | Create a loop spec (trigger / action / verifier / budget / stop) + register it. |
| `record_run.py` | Append a run entry to a loop's run log. |
| `queue_approval.py` | Append a pending approval request to the approval queue. |
| `memory_check.py` | Health-check the vault: missing/empty files, goal/approval/open-loop counts, warnings. |
| `finalize_check.py` | Pre-close gate: fails on pending approvals, un-started active goals, or unresolved open loops. |
| `loop_status.py` | Generate the plain-text and `--html` status dashboard. |

---

## 11. Session close — finalize

Before ending a working session, run the finalize gate:

```
python scripts/finalize_check.py --target <project-root>
```

It **fails** (non-zero exit) if any of these are true:
- There are **pending approvals** the user hasn't answered.
- There's an **active goal with zero completed criteria** (you opened work but proved nothing).
- There are **unresolved open loops** (un-deferred `- [ ]` items).

If it fails, don't paper over it — either resolve the items, consciously defer the open loops
with a reason, or tell the user exactly what's left and why. A clean finalize is the only honest
way to say "this session is done." Then regenerate `status.html` so the next session starts from truth.
