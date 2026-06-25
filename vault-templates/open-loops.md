# Open loops

> Threads started but not finished. Carry the real state across sessions so nothing
> silently drops. Reviewed at session start and gated at session close.

## How to use this file
- Open a loop the moment you defer something:  `- [ ] <what's unfinished> — opened <date>`
- Close it only when actually done (with evidence):  `- [x] <thing> — closed <date>`
- Consciously carrying one on purpose? Tag it so it doesn't block close:
  `- [ ] <thing> — opened <date> (deferred: <reason>)`

`finalize_check.py` fails on any un-deferred `- [ ]` here. `memory_check.py` warns above 5.

## Loops
<!-- Add items below. Example: -->
<!-- - [ ] Add rate-limit test for /api/llm/task — opened 2026-06-25 (deferred: non-gating, Wave 4) -->
