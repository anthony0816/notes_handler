#!/usr/bin/env python3
"""Gestiona el vault TODO (Obsidian + git) del usuario.

Tareas: lineas "- [ ] Titulo: descripcion" en TODO.md.
- [ ] = pendiente, - [x] = hecha. El id de cada tarea es su numero de linea.
"""

import sys

from modules.utils.todo import (
    PRIORITY_LABELS,
    SEPARATOR,
    TASK_RE,
    UNKNOWN_SEGMENT,
    current_path,
    is_segment_header,
    is_today_segment,
    parse_task,
    read_lines,
    split_priority,
    today_segment,
    write_lines,
)


def cmd_list(args):
    lines = read_lines(current_path())
    mode = "pending"
    if "--all" in args or "-a" in args:
        mode = "all"
    elif "--done" in args or "-d" in args:
        mode = "done"
    shown = False
    for i, line in enumerate(lines, 1):
        if (
            is_segment_header(line)
            or line.strip() == SEPARATOR
            or line.strip() == UNKNOWN_SEGMENT
        ):
            print(line)
            shown = True
            continue
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
    path = current_path()
    lines = read_lines(path)
    today = today_segment()
    header = None
    for i, line in enumerate(lines, 1):
        if is_today_segment(line):
            header = i
    if header is None:
        has_segments = any(is_segment_header(line) for line in lines)
        first_block = not lines
        if not has_segments and lines:
            first_task = None
            for i, line in enumerate(lines, 1):
                if parse_task(line):
                    first_task = i
                    break
            if first_task is not None:
                lines.insert(first_task - 1, UNKNOWN_SEGMENT)
        if lines and lines[-1].strip():
            lines.append("")
        if first_block:
            lines.append(f"# {path.stem}")
            lines.append("")
        else:
            lines.append(SEPARATOR)
        lines.append(today)
        lines.append(task)
    else:
        last_task = None
        for i in range(header + 1, len(lines) + 1):
            if is_segment_header(lines[i - 1]):
                break
            if parse_task(lines[i - 1]):
                last_task = i
        if last_task is None:
            last_task = header
        lines.insert(last_task, task)
    write_lines(path, lines)
    print(f"creada [{len(lines)}]: {task}")


def cmd_edit(args):
    if not args:
        sys.exit('error: usa `todo edit <id> ["p <prio>"] "nuevo texto"`')
    path = current_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args[:1])
    if not targets:
        sys.exit("no se encontro la tarea")
    rest = args[1:]
    priority = None
    if rest and rest[0] in ("p", "-p"):
        if len(rest) < 2:
            sys.exit('error: `todo edit <id> p <low|mid|max> ["nuevo texto"]`')
        label = rest[1].lower()
        if label not in PRIORITY_LABELS:
            sys.exit(f"priority state not supported, examples: {list(PRIORITY_LABELS)}")
        priority = PRIORITY_LABELS[label]
        rest = rest[2:]
    new_text = " ".join(rest)
    if priority is None and not new_text:
        sys.exit("error: falta el nuevo texto")
    i = targets[0]
    m = TASK_RE.match(lines[i - 1])
    existing, body = split_priority(m.group(3))
    if priority is not None:
        keep = body if not new_text else new_text
        new_body = f"({priority}) {keep}"
    else:
        new_body = f"({existing}) {new_text}" if existing else new_text
    lines[i - 1] = f"{m.group(1)}- [{m.group(2)}] {new_body}"
    write_lines(path, lines)
    print(f"editada [{i}]: {lines[i - 1]}")
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def cmd_toggle(args, done):
    path = current_path()
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
    path = current_path()
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
        
def cmd_zoom(args):
    if not args:
        sys.exit('error: todo zoom <id1> <id2> ...')
    lines = read_lines(current_path())
    for arg in args:
        try:
            arg = int(arg)
        except ValueError:
            print(f'{arg} - no encontrado')
            continue
        if arg < 1 or arg > len(lines):
            print(f'{arg} - no encontrado')
            continue
        print(lines[arg - 1])


USAGE = """todo - gestion de tareas TODO (Obsidian + git)

USO:
  todo create [-p low|mid|max] "Titulo" ["descripcion"]   crea tarea (prioridad default: low)
  todo list [--all|--done|--pending]     lista (default: pendientes)
  todo edit <id> ["p <prio>"] ["texto"]  edita texto (conserva prioridad); con `p` cambia prioridad
  todo done <id|texto> [otras...]        marca como hecha
  todo undo <id|texto> [otras...]        vuelve a abrir
  todo delete <id|texto> [otras...]      elimina linea(s)
  todo zoom <id1> <id2> ...              muestra el detalle completo (sin recortar)
  todo sync ["mensaje"]                  git add -A + commit + push
  todo restore [--yes]                   descarta los cambios sin commitear del vault
  todo check <nombre|main>               fija el contexto: las operaciones de tareas
                                         apuntan a ese subtodo (main = el principal)
  todo sub [create|list|delete|edit]     CRUD de subtodos (.md en subTodo/); sin
                                         argumentos lista (sub list marca con [x]
                                         el activo o main)
  todo help                              este texto

ATAJOS: add == create, rm == delete, ls == list, sub rm == sub delete.

CONTEXTO (check):
  - todo check musica -> create/list/edit/done/undo/delete/zoom operan sobre
    subTodo/musica.md hasta que se cambie; todo check main vuelve al principal.
  - todo check (sin argumentos) muestra en donde estas parado.
  - El contexto se persiste en config.json (current_sub), no en el vault.
  - sub list marca con [x] el contexto activo (main si no hay ninguno).

PRIORIDADES (create -p / edit p):
  - l / low -> (low) ; m / mid / middle -> (mid) ; max / hight -> (max)
  - todo create -p mid "Titulo" [desc] ; todo edit 3 p max ["Texto"]
  - el tag (prioridad) va al inicio del titulo y el listado con colores lo
    reemplaza por color (blanco/azul/rojo), sin mostrarlo.
  - editar el texto sin `p` mantiene la prioridad actual.

DETALLES:
  - Cada tarea es una linea: - [ ] Titulo: descripcion
  - [x] = hecha. El id es el numero de linea (puede cambiar al editar).
  - Los ids aceptan tambien busqueda por texto parcial.
  - restore: git reset --hard HEAD en el vault (pide confirmacion; --yes la saltea).
  - sub: los subtodos son .md dentro de subTodo/ (carpeta junto al
    TODO.md principal); el gestor sub NO toca el principal.
  - Al crear el primer bloque de un archivo vacio se encabeza con un H1
    con el nombre del archivo/subtodo (sin guiones al inicio).
  - restore NO borra archivos nunca commiteados: hace todo sync primero
    para que los subtodos queden trackeados.
  - Config: .env junto al script (NOTES_ROOT, NOTES_TODO opcional).
"""
