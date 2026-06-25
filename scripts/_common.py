"""Shared helpers for the claude-dev-loop scripts.

Standard library only. Imported by the other scripts via a sys.path insert of
their own directory, so it works both from the repo and from the installed skill.
"""

import datetime
import os
import re
import sys
from pathlib import Path

# Emit UTF-8 to stdout/stderr regardless of the console's legacy code page, so the
# '·'/'—' glyphs in dashboards render instead of raising UnicodeEncodeError on Windows.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

VAULT_DIRNAME = ".claude-loop"

# Files the vault is expected to contain at the top level (copied from vault-templates/,
# plus decision-log.md which bootstrap creates directly).
REQUIRED_FILES = [
    "project-brief.md",
    "preferences.md",
    "approval-gates.md",
    "approval-queue.md",
    "open-loops.md",
    "automation-registry.md",
    "decision-log.md",
]

REQUIRED_DIRS = ["goals", "loops", "runs"]


def slugify(text):
    """Lower-case, hyphenated, filesystem-safe slug."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"


def today():
    return datetime.date.today().isoformat()


def now_stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def target_root(target):
    return Path(target).expanduser().resolve()


def vault_dir(target):
    return target_root(target) / VAULT_DIRNAME


def require_vault(target):
    """Return the vault Path, or exit with a clear message if it doesn't exist."""
    vd = vault_dir(target)
    if not vd.is_dir():
        raise SystemExit(
            "error: no vault found at {}\n"
            "       run: python scripts/bootstrap_vault.py --target {}".format(vd, target)
        )
    return vd


def templates_dir():
    """Locate vault-templates/ relative to this file (repo root or installed skill root)."""
    here = Path(__file__).resolve().parent
    for cand in (here.parent / "vault-templates", here / "vault-templates"):
        if cand.is_dir():
            return cand
    return None


def read_text(path):
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def write_text(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


def append_text(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = p.read_text(encoding="utf-8") if p.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    p.write_text(existing + content, encoding="utf-8", newline="\n")


# ---------- parsing helpers (the scripts read what they write) ----------

def strip_html_comments(text):
    """Remove <!-- ... --> blocks (including multi-line) so commented examples
    in the templates are never parsed as live entries."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_field(text, field):
    """Return the value of a '- **Field:** value' line, or None."""
    m = re.search(r"^- \*\*" + re.escape(field) + r":\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return None
    # strip trailing HTML comments like '<!-- ... -->'
    val = re.sub(r"<!--.*?-->", "", m.group(1)).strip()
    return val


def section(text, heading):
    """Return the body lines under a '## heading' up to the next '## '."""
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$(.*?)(?=^##\s|\Z)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def count_checkboxes(text):
    """Return (checked, total) for GitHub-style checkboxes in text."""
    checked = len(re.findall(r"^\s*-\s*\[[xX]\]", text, re.MULTILINE))
    unchecked = len(re.findall(r"^\s*-\s*\[ \]", text, re.MULTILINE))
    return checked, checked + unchecked


def goal_files(vault):
    return sorted((vault / "goals").glob("*.md")) if (vault / "goals").is_dir() else []


def loop_files(vault):
    return sorted((vault / "loops").glob("*.md")) if (vault / "loops").is_dir() else []


def load_goal(path):
    text = read_text(path)
    checked, total = count_checkboxes(section(text, "Done criteria"))
    return {
        "slug": parse_field(text, "Slug") or path.stem,
        "title": _title(text, "Goal"),
        "status": (parse_field(text, "Status") or "active").lower(),
        "checked": checked,
        "total": total,
        "path": path,
    }


def load_loop(path, vault):
    text = read_text(path)
    slug = parse_field(text, "Slug") or path.stem
    runs_file = vault / "runs" / (slug + "-runs.md")
    run_count, last_verifier = _run_stats(runs_file)
    return {
        "slug": slug,
        "title": _title(text, "Loop"),
        "status": (parse_field(text, "Status") or "active").lower(),
        "budget": parse_field(text, "Budget") or "",
        "runs": run_count,
        "last_verifier": last_verifier,
        "path": path,
    }


def _title(text, kind):
    m = re.search(r"^#\s+" + kind + r":\s*(.+?)\s*$", text, re.MULTILINE)
    return m.group(1) if m else "(untitled)"


def _run_stats(runs_file):
    text = read_text(runs_file)
    if not text:
        return 0, None
    stamps = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2}.*)$", text, re.MULTILINE)
    verifiers = re.findall(r"^- \*\*Verifier:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    last = verifiers[-1] if verifiers else None
    return len(stamps), last


def pending_approvals(vault):
    """Return a list of pending approval titles from approval-queue.md."""
    text = strip_html_comments(read_text(vault / "approval-queue.md"))
    titles = []
    # An entry is '## [pending] Title' followed (somewhere) by '- **Status:** pending'.
    for m in re.finditer(r"^##\s+\[pending\]\s+(.+?)\s*$", text, re.MULTILINE):
        titles.append(m.group(1))
    # Fall back to counting status lines if headings use a different style.
    if not titles:
        n = len(re.findall(r"^- \*\*Status:\*\*\s*pending\s*$", text, re.MULTILINE | re.IGNORECASE))
        titles = ["(pending approval)"] * n
    return titles


def open_loops(vault):
    """Return (unresolved, deferred) lists of open-loop descriptions."""
    text = strip_html_comments(read_text(vault / "open-loops.md"))
    unresolved, deferred = [], []
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*\[ \]\s*(.+?)\s*$", line)
        if not m:
            continue
        desc = m.group(1)
        if "(deferred" in desc.lower():
            deferred.append(desc)
        else:
            unresolved.append(desc)
    return unresolved, deferred
