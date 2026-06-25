# Loop patterns: what makes a good loop (and what makes a "wish")

Loops are the heart of the self-verifying part of claude-dev-loop, and they're also the easiest thing to get wrong. This thread is for collecting good and bad patterns so we all write sharper ones.

## The one rule that matters

From `CLAUDE.md`:

> A loop with no verifier is not a loop — it's a wish. If you can't state how an iteration is checked, don't create the loop.

A loop is a recurring task with a **contract**: it knows when to run, what to do, **how to check itself**, how much budget it gets, and when to stop. The check — the **verifier** — has to be *runnable*. If the only way to know whether an iteration succeeded is "it looks done," that's a wish, not a loop.

## The five fields

You create a loop with `create_loop.py`, and a spec lands in `.claude-loop/loops/<slug>.md` with these parts:

- **Trigger** — when this loop should run.
- **Action** — what you do on each iteration, concrete and bounded.
- **Verifier** — the objective check that says whether the iteration succeeded. **Must be runnable.**
- **Budget** — how much it gets (e.g. "5 runs" or "until done criteria met" — that string is the default if you omit `--budget`).
- **Stop condition** — when to stop looping: success, budget exhausted, or escalate.

And the discipline that makes loops trustworthy: **every iteration must be recorded as a run** with `record_run.py`, where the `--result` line reflects the *actual* verifier result — including failures. A run log that's all `PASS` and never a `FAIL` is a red flag, not a success story.

## Good example: a nightly test gate

```powershell
py scripts\create_loop.py --target . --title "Nightly test gate" `
  --trigger "Each session start, or after any backend change" `
  --action "Run the full test suite and clippy" `
  --verifier "All tests green AND clippy -D warnings clean" `
  --budget "1 run per change; stop after 3 consecutive failures" `
  --stop "Green build with 0 warnings, or escalate after 3 failures"
```

Why it's good:

- The **verifier is a real command** with a binary outcome — tests are green or they aren't; clippy is clean or it isn't.
- The **action is bounded** ("run the suite and clippy"), not open-ended ("improve the tests").
- The **stop condition is concrete** and ties into stall detection: the same verifier failing 3 times with the same root cause means stop and diagnose, don't blindly retry a 4th time.

Then each iteration gets recorded honestly:

```powershell
py scripts\record_run.py --target . --loop nightly-test-gate `
  --observed "guardrails.rs changed" --action "ran cargo test --lib and clippy" `
  --result "PASS — 97 passed; clippy clean" --next "none"
```

…and a failing run is recorded just as plainly:

```powershell
py scripts\record_run.py --target . --loop nightly-test-gate `
  --observed "auth module changed" --action "ran cargo test --lib" `
  --result "FAIL — 2 failed in auth::session; token TTL off by one" `
  --next "fix TTL math, rerun (failure 1 of 3 before escalate)"
```

## Bad example: a wish dressed up as a loop

```
Title:    Make the app feel polished
Trigger:  Whenever I think about it
Action:   Improve the UI and fix anything that seems off
Verifier: It looks good
Budget:   (none)
Stop:     When it's done
```

Why it's a wish, not a loop:

- **"It looks good" isn't runnable.** There's no command, no on-screen observation you could record as a PASS/FAIL — so every run log entry would be a self-graded "PASS" with nothing behind it.
- **The action is unbounded.** "Improve anything that seems off" has no edge; it can't converge.
- **The trigger and stop are vibes**, not conditions. "Whenever I think about it" / "when it's done" gives the loop no way to know when to fire or when to quit.

Don't create this loop. Either find a runnable verifier (e.g. "axe-core reports 0 critical a11y violations on the settings page," or "the 4 screenshots in `/qa` match approved baselines") and a bounded action — or keep it as a goal/open-loop note instead.

## Turning a wish into a loop

The fix is almost always: **replace the subjective verifier with a runnable one.**

| Wish verifier | Runnable verifier |
|---|---|
| "Tests are in good shape" | "`cargo test --lib` exits 0 with 0 failures" |
| "No obvious lint problems" | "`clippy -D warnings` is clean" |
| "Docs are up to date" | "`markdown-link-check` finds 0 broken links in `/docs`" |
| "The build is fine" | "`npm run build` exits 0 and emits `dist/index.html`" |

If you can't write the right-hand column, you don't yet have a loop — and that's useful information, not a failure.

## Share yours

Post a loop spec you're happy with — or one you *thought* was a loop until you tried to write the verifier and realized it was a wish. Both are great teaching examples.
