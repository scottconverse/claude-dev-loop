# Approval queue

> Gated actions Claude has surfaced and is waiting on the user to approve or deny.
> Append new requests with `scripts/queue_approval.py`. Newest at the bottom.
>
> An entry is **pending** until the user answers. When approved/denied, change its
> heading from `## [pending]` to `## [approved]` or `## [denied]`, flip `Status:`,
> and log the outcome in `decision-log.md`.

<!-- Entries are appended below this line. Example of the shape: -->

<!--
## [pending] Push remediation branch
- **Requested:** 2026-06-25 14:30:00
- **Action:** git push origin gauntletgate-remediation
- **Reason:** 4 commits ready for the user's independent review
- **Risk:** low — publishes the branch to the user's GitHub
- **Status:** pending
-->
