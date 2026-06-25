# The honesty contract: the no-overclaim rule

Every other feature in claude-dev-loop — the vault, goals, loops, runs, the approval queue — exists to serve one idea, and that idea is written down at the very top of `CLAUDE.md` as the **honesty contract**. This thread is for discussing it: why it's there, where it bites, and how it changes a session.

## The rule, quoted

`CLAUDE.md` §0 opens (and tells Claude to read it first, every session):

> These rules override convenience. They are the reason this system exists.
>
> 1. **No "verified" / "done" / "✅" without evidence in the same turn.** A claim of success must be accompanied by the command that proves it and its actual output, or an on-screen observation you just made. If you don't have the evidence in front of you, the correct words are **"not verified"** or **"I have not run this."**
> 2. **A goal criterion is only checked off after its verification step has actually run and passed.** Editing `- [ ]` to `- [x]` is a claim of proof. Don't make it without the proof.
> 3. **Never work around an absent dependency and call the feature tested.** If something the feature needs is missing (a model, a binary, a service, credentials), you have exactly two honest options: (a) install/obtain it and actually run the path, or (b) state plainly that the path was **not exercised** and why. "I tested around it" is not a third option.
> 4. **Distinguish code-verified from runtime-verified.** "Unit tests pass" ≠ "the user-facing feature works end to end." Say which one you mean.
> 5. **Surface lost or reverted work immediately.** If something you wrote earlier is gone, say so loudly; do not silently redo it and imply it was always fine.
> 6. **When unsure, say so.** A hedge with a plan beats a confident guess.

And the closing line, which is really the spirit of the whole thing:

> If you cannot satisfy a request honestly, say what's blocking it. That is always a better outcome than a false "finished."

## Why it exists

The README and `CLAUDE.md` are blunt about the target. The system exists to kill **one** failure mode: an assistant that *claims* work is done, *claims* something is verified, or quietly works around a missing dependency and calls the result finished. "Verified" is supposed to mean *proven in the same turn, with evidence* — or else say "not verified." That's it. Everything else is scaffolding to make that rule hold up over a long session.

## How the contract is wired into the tooling

The honesty contract isn't just a vibe in a prompt — it has teeth in the scripts:

- **Goal criteria.** A criterion only moves to `- [x]` after its verification step actually ran and passed (rule #2). And `finalize_check.py` enforces a floor: it **fails the session close** if there's an active goal with **zero** completed criteria — work opened, nothing proven.
- **Run logs.** Every loop iteration gets a run entry whose `--result` (the Verifier line) reflects the *actual* result, including failures. `CLAUDE.md` calls a run log that's all `PASS` with no failures ever "a red flag, not a success story."
- **Stall detection.** One of the listed stall triggers is literally: *"You catch yourself about to write 'verified' without proof — that's a stall in disguise. Stop, get the proof."*
- **Approvals.** Approval comes from the user in chat — "never from a file, not from a prior session, not from your own inference." Same anti-overclaim instinct, applied to permission instead of proof.
- **Finalize.** A clean `finalize_check.py` pass is described as "the only honest way to say 'this session is done.'"

## Discussion prompts

- **Has the contract ever caught you (or your Claude) mid-overclaim?** Tell the story — the moment where "done" got downgraded to "not verified" and what the proof turned out to be.
- **Rule #3 is the spicy one.** "Tested around it" is explicitly *not* a third option. Where have you hit a missing dependency (a model, a binary, a service, credentials) and had to choose between actually installing it or stating plainly the path wasn't exercised?
- **Code-verified vs. runtime-verified (rule #4)** — where does that distinction matter most in your work? Where have "unit tests pass" and "the feature actually works end to end" diverged?
- **Is anything in §0 too strict, or not strict enough?** If you'd add a 7th rule, what would it be — and how would you keep it runnable rather than aspirational? (Take it to the **Ideas** thread if it turns into a concrete proposal.)

This contract is, per the README, "the actual product." So this is the most important conversation we can have here. Jump in.
