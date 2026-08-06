#!/usr/bin/env python3
"""Gestiona el vault TODO (Obsidian + git) del usuario.

Tareas: lineas "- [ ] Titulo: descripcion" en TODO.md.
- [ ] = pendiente, - [x] = hecha. El id de cada tarea es su numero de linea.
"""

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"
DEFAULT_NOTE_ROOT = Path("C:/Antonio/Notes")
DEFAULT_TODO_REL = "TODO/TODO/TODO.md"

TASK_RE = re.compile(r"^(\s*)- \[([ xX])\](.*)$")


def load_env():
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


ENV = load_env()


def notes_root():
    raw = os.environ.get("NOTES_ROOT") or ENV.get("NOTES_ROOT")
    return Path(raw) if raw else DEFAULT_NOTE_ROOT


def todo_path():
    raw = os.environ.get("NOTES_TODO") or ENV.get("NOTES_TODO")
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


def task_text(line):
    parsed = parse_task(line)
    return parsed[2] if parsed else None


def cmd_list(args):
    lines = read_lines(todo_path())
    mode = "pending"
    if "--all" in args or "-a" in args:
        mode = "all"
    elif "--done" in args or "-d" in args:
        mode = "done"
    shown = False
    for i, line in enumerate(lines, 1):
        parsed = parse_task(line)
        if not parsed:
            continue
        done, _, text = parsed
        if show_filter(done, mode):
            print(f"{i:4}  {line}")
            shown = True
    if not shown:
        print("(sin tareas)")


def show_filter(done, mode):
    if mode == "all":
        return True
    if mode == "done":
        return done
    return not done


def find_targets(lines, args):
    targets = []
    unknown = []
    for arg in args:
        if arg.isdigit():
            n = int(arg)
            if 1 <= n <= len(lines):
                targets.append(n)
            else:
                unknown.append(f"id {n}")
        else:
            matches = [i for i, l in enumerate(lines, 1) if arg.lower() in l.lower()]
            if matches:
                targets.extend(matches)
            else:
                unknown.append(f"'{arg}'")
    targets = sorted(set(t for t in targets if parse_task(lines[t - 1])))
    return targets, unknown


def cmd_create(args):
    if not args:
        sys.exit('error: usa `todo create "Titulo" ["descripcion"]`')
    title = args[0]
    desc = " ".join(args[1:])
    task = f"- [ ] {title}" + (f": {desc}" if desc else "")
    path = todo_path()
    lines = read_lines(path)
    lines.append(task)
    write_lines(path, lines)
    print(f"creada [{len(lines)}]: {task}")


def cmd_edit(args):
    if not args:
        sys.exit('error: usa `todo edit <id> "nuevo texto"`')
    path = todo_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args[:1])
    if not targets:
        sys.exit("no se encontro la tarea")
    new_text = " ".join(args[1:])
    if not new_text:
        sys.exit("error: falta el nuevo texto")
    i = targets[0]
    m = TASK_RE.match(lines[i - 1])
    lines[i - 1] = f"{m.group(1)}- [{m.group(2)}] {new_text}"
    write_lines(path, lines)
    print(f"editada [{i}]: {lines[i - 1]}")
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def cmd_toggle(args, done):
    path = todo_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args)
    if not targets:
        sys.exit("no se encontro la tarea")
    mark = "x" if done else " "
    for i in targets:
        m = TASK_RE.match(lines[i - 1])
        lines[i - 1] = f"{m.group(1)}- [{mark}]{m.group(3)}"
    write_lines(path, lines)
    for i in targets:
        verb = "hecha" if done else "reabierta"
        print(f"{verb} [{i}]: {lines[i - 1]}")
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def cmd_delete(args):
    path = todo_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args)
    if not targets:
        sys.exit("no se encontro la tarea")
    for i in sorted(targets, reverse=True):
        print(f"eliminada [{i}]: {lines[i - 1]}")
        del lines[i - 1]
    write_lines(path, lines)
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def run_git(root, args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8"
    )


def cmd_sync(args):
    root = notes_root()
    if not (root / ".git").exists():
        sys.exit(f"error: no es repo git: {root}")
    message = " ".join(args) or f"notas: {datetime.datetime.now():%Y-%m-%d %H:%M}"
    add = run_git(root, ["add", "-A"])
    if "error" in add.stderr.lower():
        sys.exit(f"git add fallo: {add.stderr}")
    commit = run_git(root, ["commit", "-m", message])
    if commit.returncode != 0:
        if "nothing to commit" in commit.stdout.lower():
            print("nada que commitear")
            return
        sys.exit(f"git commit fallo: {commit.stderr or commit.stdout}")
    print(commit.stdout.strip())
    push = run_git(root, ["push"])
    if push.returncode != 0:
        sys.exit(f"git push fallo: {push.stderr or push.stdout}")
    print(push.stdout.strip())


USAGE = """todo - gestion de tareas TODO (Obsidian + git)

USO:
  todo create "Titulo" ["descripcion"]    crea tarea
  todo list [--all|--done|--pending]     lista (default: pendientes)
  todo edit <id> "nuevo texto"           reemplaza titulo/descripcion
  todo done <id|texto> [otras...]        marca como hecha
  todo undo <id|texto> [otras...]        vuelve a abrir
  todo delete <id|texto> [otras...]      elimina linea(s)
  todo sync ["mensaje"]                  git add -A + commit + push
  todo help                              este texto

ATAJOS: add == create, rm == delete, ls == list.

DETALLES:
  - Cada tarea es una linea: - [ ] Titulo: descripcion
  - [x] = hecha. El id es el numero de linea (puede cambiar al editar).
  - Los ids aceptan tambien busqueda por texto parcial.
  - Config: .env junto al script (NOTES_ROOT) o variable de entorno.
"""


def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(USAGE)
        return
    cmd, args = argv[0].lower(), argv[1:]
    if cmd == "list" or cmd == "ls":
        cmd_list(args)
    elif cmd == "create" or cmd == "add":
        cmd_create(args)
    elif cmd == "edit":
        cmd_edit(args)
    elif cmd == "done":
        cmd_toggle(args, done=True)
    elif cmd == "undo":
        cmd_toggle(args, done=False)
    elif cmd == "delete" or cmd == "rm":
        cmd_delete(args)
    elif cmd == "sync":
        cmd_sync(args)
    else:
        sys.exit(f"comando desconocido: {cmd}\n\n{USAGE}")


if __name__ == "__main__":
    main(sys.argv[1:])