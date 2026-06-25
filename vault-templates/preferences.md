# Preferences

> How the user wants Claude to work on this project. Loaded every session. Honor it.
> If a request conflicts with something here, surface the conflict instead of silently choosing.

## Autonomy level
_How much should Claude do before checking in?_
- [ ] Tight leash — confirm before each substantive step.
- [ ] Balanced — proceed on clearly-scoped work; ask at decision points.
- [ ] Long leash — drive to done; only stop for gated actions and real ambiguity.

## Communication
- **Tone:** _direct / detailed / terse — pick one._
- **Show your evidence:** always include the command + real output behind any "done"/"passed" claim.
- **No overclaiming:** label code-verified vs. runtime-verified; never write "verified" without proof in the same turn.
- **Surface lost work loudly** rather than silently redoing it.

## Stack & conventions
- **Languages / frameworks:**
- **Build / test commands:**
- **Formatting / lint:**
- **Branching:** _e.g. work on a branch; never commit to main without asking._

## Do
- _Things the user explicitly wants (write tests first, keep diffs small, etc.)._

## Don't
- _Things the user has explicitly ruled out._

## Hard-won lessons (this project)
- _Add entries as you learn what trips Claude up here, so the next session avoids it._
