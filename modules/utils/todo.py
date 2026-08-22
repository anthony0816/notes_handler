import datetime
import re
import sys
from pathlib import Path

from modules.config.config import get as config_get
from modules.env.env import load_env

DEFAULT_TODO_REL = "TODO/TODO.md"
TASK_RE = re.compile(r"^(\s*)- \[([ xX])\](.*)$")
PRIORITY_RE = re.compile(r"^\(\s*(low|mid|max)\s*\)\s*(.*)$", re.IGNORECASE)
PRIORITY_LABELS = {
    "l": "low",
    "low": "low",
    "m": "mid",
    "mid": "mid",
    "middle": "mid",
    "max": "max",
    "hight": "max",
}
DATE_RE = re.compile(r"^##\s*(\d{4})/(\d{1,2})/(\d{1,2})\s*$")
DATE_RE_DMY = re.compile(r"^##\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")
SEPARATOR = "---"
UNKNOWN_SEGMENT = "## Unknown Date"
ENV = load_env()


def notes_root():
    raw = ENV.get("NOTES_ROOT")
    if not raw:
        sys.exit(
            "error: falta NOTES_ROOT (en .env). "
            "Copia .env.example a .env y ajusta la ruta."
        )
    return Path(raw)


def todo_path():
    raw = ENV.get("NOTES_TODO")
    if raw:
        rel = Path(raw)
        return rel if rel.is_absolute() else notes_root() / rel
    return notes_root() / DEFAULT_TODO_REL


def sub_path(name):
    if not name or any(c in name for c in "/\\:") or name in (".", ".."):
        sys.exit(f"error: nombre invalido: {name}")
    return todo_path().parent / "subTodo" / f"{name}.md"


def current_sub():
    return config_get("current_sub")


def current_path():
    name = current_sub()
    if not name:
        return todo_path()
    path = sub_path(name)
    if not path.exists():
        sys.exit(f"error: no existe el subtodo: {name}")
    return path


def read_lines(path):
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def write_lines(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_task(line):
    m = TASK_RE.match(line)
    if not m:
        return None
    done = m.group(2).lower() == "x"
    return done, m.group(1), m.group(3).strip()


def split_task_text(text):
    title, sep, desc = text.partition(":")
    if not sep:
        return text.strip(), ""
    return title.strip(), desc.strip()


def split_priority(text):
    m = PRIORITY_RE.match(text.strip())
    if m:
        return m.group(1).lower(), m.group(2).strip()
    return None, text.strip()


def filter_task(done, mode):
    if mode == "all":
        return True
    if mode == "done":
        return done
    return not done


def mode_from_args(args):
    if "--all" in args or "-a" in args:
        return "all"
    if "--done" in args or "-d" in args:
        return "done"
    return "pending"


def task_line_numbers(lines):
    return [i for i, line in enumerate(lines, 1) if parse_task(line)]


def line_to_id(lines):
    return {line_no: n for n, line_no in enumerate(task_line_numbers(lines), 1)}


def todo_items(path=None):
    lines = read_lines(path or todo_path())
    items = []
    for n, i in enumerate(task_line_numbers(lines), 1):
        done, _, text = parse_task(lines[i - 1])
        items.append({"id": n, "num": i, "done": done, "line": lines[i - 1], "text": text})
    return items


#======= Time Segmentation ===========

def today_segment():
    d = datetime.date.today()
    return f"## {d.year}/{d.month}/{d.day}"


def segment_title(line):
    parts = segment_date(line)
    if not parts:
        return None
    y, mo, d = parts
    return f"{y}/{mo}/{d}"


def segment_date(line):
    m = DATE_RE.match(line)
    if m:
        y, mo, d = (int(x) for x in m.groups())
    else:
        m = DATE_RE_DMY.match(line)
        if not m:
            return None
        d, mo, y = (int(x) for x in m.groups())
    try:
        datetime.date(y, mo, d)
    except ValueError:
        return None
    return (y, mo, d)


def is_segment_header(line):
    return segment_date(line) is not None


def is_today_segment(line):
    d = segment_date(line)
    if not d:
        return False
    t = datetime.date.today()
    return d == (t.year, t.month, t.day)


def parse_segments(lines):
    segments = []
    current = {"date": None, "task_idx": []}
    for i, line in enumerate(lines, 1):
        if is_segment_header(line) or line.strip() == UNKNOWN_SEGMENT:
            segments.append(current)
            current = {"date": line, "task_idx": []}
        elif parse_task(line):
            current["task_idx"].append(i)
    segments.append(current)
    return segments