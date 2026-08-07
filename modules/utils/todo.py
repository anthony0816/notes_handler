import re
import sys
from pathlib import Path

from modules.env.env import load_env

DEFAULT_TODO_REL = "TODO/TODO.md"
TASK_RE = re.compile(r"^(\s*)- \[([ xX])\](.*)$")
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


def todo_items():
    items = []
    for i, line in enumerate(read_lines(todo_path()), 1):
        parsed = parse_task(line)
        if parsed:
            done, _, text = parsed
            items.append({"id": i, "done": done, "line": line, "text": text})
    return items
