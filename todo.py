#!/usr/bin/env python3
"""Gestiona el vault TODO (Obsidian + git) del usuario.

Tareas: lineas "- [ ] Titulo: descripcion" en TODO.md.
- [ ] = pendiente, - [x] = hecha. El id de cada tarea es su numero de linea.
"""

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
