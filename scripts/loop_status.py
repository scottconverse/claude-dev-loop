#!/usr/bin/env python3
"""Generate a status dashboard for a .claude-loop/ vault.

Plain-text summary to stdout by default; with --html, also writes a self-contained
dark-themed dashboard to .claude-loop/status.html (no external dependencies).

Usage:
    python scripts/loop_status.py --target <root>
    python scripts/loop_status.py --target <root> --html
"""

import argparse
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    goal_files,
    load_goal,
    load_loop,
    loop_files,
    now_stamp,
    open_loops,
    pending_approvals,
    require_vault,
)

STATUS_COLORS = {
    "active": "#4aa3ff",
    "done": "#3ecf8e",
    "blocked": "#ff6b6b",
    "abandoned": "#8a8f98",
    "paused": "#f1c40f",
}


def gather(vault):
    goals = [load_goal(p) for p in goal_files(vault)]
    loops = [load_loop(p, vault) for p in loop_files(vault)]
    pending = pending_approvals(vault)
    unresolved, deferred = open_loops(vault)
    return goals, loops, pending, unresolved, deferred


# ---------------- plain text ----------------

def render_text(vault, goals, loops, pending, unresolved, deferred):
    out = []
    out.append("=" * 60)
    out.append("  claude-dev-loop status — {}".format(vault.parent.name))
    out.append("  generated {}".format(now_stamp()))
    out.append("=" * 60)

    out.append("\nGOALS ({})".format(len(goals)))
    if not goals:
        out.append("  (none)")
    for g in goals:
        pct = int(round(100 * g["checked"] / g["total"])) if g["total"] else 0
        out.append("  [{:<9}] {}  ({}/{} · {}%)".format(
            g["status"], g["title"], g["checked"], g["total"], pct))

    out.append("\nLOOPS ({})".format(len(loops)))
    if not loops:
        out.append("  (none)")
    for l in loops:
        lv = l["last_verifier"] or "—"
        out.append("  [{:<9}] {}  · {} run(s) · last: {}".format(
            l["status"], l["title"], l["runs"], lv))

    out.append("\nPENDING APPROVALS ({})".format(len(pending)))
    if not pending:
        out.append("  (none)")
    for t in pending:
        out.append("  - {}".format(t))

    out.append("\nOPEN LOOPS ({} unresolved · {} deferred)".format(len(unresolved), len(deferred)))
    if not unresolved and not deferred:
        out.append("  (none)")
    for d in unresolved:
        out.append("  - [ ] {}".format(d))
    for d in deferred:
        out.append("  - [~] {}".format(d))

    out.append("")
    return "\n".join(out)


# ---------------- html ----------------

def _badge(status):
    color = STATUS_COLORS.get(status, "#8a8f98")
    return '<span class="badge" style="background:{}1a;color:{};border:1px solid {}55">{}</span>'.format(
        color, color, color, html.escape(status))


def _bar(checked, total):
    pct = int(round(100 * checked / total)) if total else 0
    color = "#3ecf8e" if pct == 100 else "#4aa3ff"
    return (
        '<div class="bar"><div class="fill" style="width:{}%;background:{}"></div></div>'
        '<span class="pct">{}/{} · {}%</span>'
    ).format(pct, color, checked, total, pct)


def render_html(vault, goals, loops, pending, unresolved, deferred):
    project = html.escape(vault.parent.name)

    goal_rows = []
    for g in goals:
        goal_rows.append(
            '<div class="row"><div class="rhead">{} <span class="title">{}</span></div>'
            '<div class="prog">{}</div></div>'.format(
                _badge(g["status"]), html.escape(g["title"]), _bar(g["checked"], g["total"]))
        )
    if not goals:
        goal_rows.append('<div class="empty">No goals yet.</div>')

    loop_rows = []
    for l in loops:
        lv = html.escape(l["last_verifier"] or "—")
        loop_rows.append(
            '<div class="row"><div class="rhead">{} <span class="title">{}</span></div>'
            '<div class="meta">{} run(s) · last verifier: <span class="mono">{}</span></div></div>'.format(
                _badge(l["status"]), html.escape(l["title"]), l["runs"], lv)
        )
    if not loops:
        loop_rows.append('<div class="empty">No loops yet.</div>')

    appr_rows = "".join('<li>{}</li>'.format(html.escape(t)) for t in pending) \
        or '<li class="empty">No pending approvals.</li>'

    ol_items = "".join('<li class="open">{}</li>'.format(html.escape(d)) for d in unresolved)
    ol_items += "".join('<li class="deferred">{} <em>(deferred)</em></li>'.format(html.escape(d)) for d in deferred)
    ol_items = ol_items or '<li class="empty">No open loops.</li>'

    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>claude-dev-loop · {project}</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         background:#0d1117; color:#e6edf3; line-height:1.5; }}
  .wrap {{ max-width:920px; margin:0 auto; padding:32px 20px 64px; }}
  header h1 {{ font-size:20px; margin:0 0 4px; }}
  header .sub {{ color:#8a8f98; font-size:13px; margin-bottom:28px; }}
  h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:#8a8f98;
        border-bottom:1px solid #21262d; padding-bottom:8px; margin:32px 0 14px; }}
  .row {{ background:#161b22; border:1px solid #21262d; border-radius:8px; padding:12px 14px; margin-bottom:8px; }}
  .rhead {{ display:flex; align-items:center; gap:10px; }}
  .title {{ font-weight:600; }}
  .badge {{ font-size:11px; padding:2px 9px; border-radius:999px; text-transform:uppercase; letter-spacing:.04em; }}
  .prog {{ display:flex; align-items:center; gap:10px; margin-top:10px; }}
  .bar {{ flex:1; height:8px; background:#21262d; border-radius:999px; overflow:hidden; }}
  .fill {{ height:100%; border-radius:999px; }}
  .pct {{ font-size:12px; color:#8a8f98; white-space:nowrap; }}
  .meta {{ font-size:12px; color:#8a8f98; margin-top:8px; }}
  .mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; color:#c9d1d9; }}
  ul {{ list-style:none; padding:0; margin:0; }}
  li {{ background:#161b22; border:1px solid #21262d; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:14px; }}
  li.open {{ border-left:3px solid #ff6b6b; }}
  li.deferred {{ border-left:3px solid #f1c40f; color:#b9c0c8; }}
  li.deferred em, li.empty {{ color:#8a8f98; }}
  .empty {{ color:#8a8f98; font-style:italic; }}
  .counts {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px; }}
  .chip {{ background:#161b22; border:1px solid #21262d; border-radius:6px; padding:4px 10px; font-size:12px; color:#8a8f98; }}
  .chip b {{ color:#e6edf3; }}
  footer {{ margin-top:40px; color:#8a8f98; font-size:12px; }}
</style></head>
<body><div class="wrap">
  <header>
    <h1>claude-dev-loop · {project}</h1>
    <div class="sub">generated {stamp}</div>
    <div class="counts">
      <span class="chip"><b>{ngoals}</b> goals</span>
      <span class="chip"><b>{nloops}</b> loops</span>
      <span class="chip"><b>{npending}</b> pending approvals</span>
      <span class="chip"><b>{nopen}</b> open loops</span>
    </div>
  </header>

  <h2>Goals</h2>
  {goal_rows}

  <h2>Loops</h2>
  {loop_rows}

  <h2>Pending approvals</h2>
  <ul>{appr_rows}</ul>

  <h2>Open loops</h2>
  <ul>{ol_items}</ul>

  <footer>Generated by loop_status.py — do not hand-edit; re-run the script.</footer>
</div></body></html>
""".format(
        project=project,
        stamp=now_stamp(),
        ngoals=len(goals),
        nloops=len(loops),
        npending=len(pending),
        nopen=len(unresolved),
        goal_rows="\n  ".join(goal_rows),
        loop_rows="\n  ".join(loop_rows),
        appr_rows=appr_rows,
        ol_items=ol_items,
    )


def main():
    ap = argparse.ArgumentParser(description="Generate the status dashboard.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    ap.add_argument("--html", action="store_true", help="also write .claude-loop/status.html")
    args = ap.parse_args()

    vault = require_vault(args.target)
    goals, loops, pending, unresolved, deferred = gather(vault)

    print(render_text(vault, goals, loops, pending, unresolved, deferred))

    if args.html:
        out = vault / "status.html"
        out.write_text(
            render_html(vault, goals, loops, pending, unresolved, deferred),
            encoding="utf-8",
            newline="\n",
        )
        print("HTML dashboard written: {}".format(out))


if __name__ == "__main__":
    main()
