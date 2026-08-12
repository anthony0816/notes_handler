#!/usr/bin/env python3
"""Gestiona el vault TODO (Obsidian + git) del usuario.

Tareas: lineas "- [ ] Titulo: descripcion" en TODO.md.
- [ ] = pendiente, - [x] = hecha. El id de cada tarea es su numero de linea.
"""

import sys

from modules.utils.todo import TASK_RE, parse_task, read_lines, todo_path, write_lines


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
    priority_flags = ['p', '-p']
    priority_labels = ['low','l','m','mid','middle', 'max', 'hight']
    priority_dic = {
        priority_labels[0] : 'low', 
        priority_labels[1] : "low",
        priority_labels[2] : "mid", 
        priority_labels[3] : "mid",
        priority_labels[4] : "mid",
        priority_labels[5] : "max",
        priority_labels[6] : "max"
    }
    if not args:
        sys.exit('error: usa `todo create "Titulo" ["descripcion"]`')
    title = args[0]
    desc = " ".join(args[1:])
    priority =  'low'
    
    if args[0].lower() in priority_flags:
        if args[1].lower() not in priority_labels : 
            return  print(f'Priority state not suported, examples: {priority_labels.__str__()}')
        title = args[2]
        desc = " ".join(args[3:])
        priority = priority_dic.get(args[1].lower())
    
    task = f"- [ ] ({priority}) {title}" + (f": {desc}" if desc else "")
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
  todo create [-p low|mid|max] "Titulo" ["descripcion"]   crea tarea (prioridad default: low)
  todo list [--all|--done|--pending]     lista (default: pendientes)
  todo edit <id> "nuevo texto"           reemplaza titulo/descripcion
  todo done <id|texto> [otras...]        marca como hecha
  todo undo <id|texto> [otras...]        vuelve a abrir
  todo delete <id|texto> [otras...]      elimina linea(s)
  todo sync ["mensaje"]                  git add -A + commit + push
  todo help                              este texto

ATAJOS: add == create, rm == delete, ls == list.

PRIORIDADES (create -p):
  - l / low -> (low) ; m / mid / middle -> (mid) ; max / hight -> (max)
  - el tag (prioridad) va al inicio del titulo y el listado con colores lo
    reemplaza por color (blanco/azul/rojo), sin mostrarlo.

DETALLES:
  - Cada tarea es una linea: - [ ] Titulo: descripcion
  - [x] = hecha. El id es el numero de linea (puede cambiar al editar).
  - Los ids aceptan tambien busqueda por texto parcial.
  - Config: .env junto al script (NOTES_ROOT, NOTES_TODO opcional).
"""
