#!/usr/bin/env python3
"""Gestiona el vault TODO (Obsidian + git) del usuario.

Tareas: lineas "- [ ] H:MM AM/PM (prioridad) Titulo: descripcion" en TODO.md.
- [ ] = pendiente, - [x] = hecha. El id es el ordinal de la tarea.
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
    split_task_lines,
    split_task_meta,
    task_blocks,
    task_line_numbers,
    task_ranges,
    line_to_id,
    today_segment,
    today_time,
    write_lines,
    create_task_block_from_title_desc_time_priority
)


def cmd_list(args):
    lines = read_lines(current_path())
    mode = "pending"
    if "--all" in args or "-a" in args:
        mode = "all"
    elif "--done" in args or "-d" in args:
        mode = "done"
    shown = False
    n = 0
    block_ends = {s: e for s, e in task_ranges(lines)}
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
        n += 1
        done, _, text = parsed
        if show_filter(done, mode):
            suffix = " ...more" if block_ends.get(i, i) > i else ""
            print(f"{n:4}  {line}{suffix}")
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
    ids = task_line_numbers(lines)
    targets = []
    unknown = []
    for arg in args:
        if arg.isdigit():
            n = int(arg)
            if 1 <= n <= len(ids):
                targets.append(ids[n - 1])
            else:
                unknown.append(f"id {n}")
        else:
            unknown.append(f"'{arg}'")
    targets = sorted(set(targets))
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
    title = args[0].replace("\\n", "\n")
    desc = " ".join(args[1:]).replace("\\n", "\n")
    priority =  'low'
    
    if args[0].lower() in priority_flags:
        if args[1].lower() not in priority_labels : 
            return  print(f'Priority state not suported, examples: {priority_labels.__str__()}')
        title = args[2].replace("\\n", "\n")
        desc = " ".join(args[3:]).replace("\\n", "\n")
        priority = priority_dic.get(args[1].lower())
    
    time = today_time()
    
    block = create_task_block_from_title_desc_time_priority(title, desc, time, priority)
    
    path = current_path()
    lines = read_lines(path)
    segment = today_segment()
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
        lines.append(segment)
        lines.extend(block)
        pos = len(lines) - len(block) + 1
    else:
        blocks = task_blocks(lines)
        last_task_end = header
        for i in range(header + 1, len(lines) + 1):
            if is_segment_header(lines[i - 1]):
                break
            if parse_task(lines[i - 1]):
                last_task_end = blocks[i][1]
        lines[last_task_end:last_task_end] = block
        pos = last_task_end + 1
    write_lines(path, lines)
    new_id = line_to_id(lines)[pos]
    print(f"creada [{new_id}]:")
    for ln in block:
        print(f"  {ln}")


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
    title = None
    desc =  None
    if rest:
        title = rest[0].replace("\\n", "\n")
        desc = " ".join(rest[1:]).replace("\\n", "\n")
        
    if priority is None and not rest:
        sys.exit("error: falta el nuevo texto")
    i = targets[0]
    blocks = task_blocks(lines)
    start_block, end_block = blocks[i]
    n = line_to_id(lines)[i]
    m = TASK_RE.match(lines[i - 1])
    time_str, existing_priority, body = split_task_meta(m.group(3).strip())
    final_priority = priority if priority else existing_priority
    if title is None and desc is None:
        if existing_priority and existing_priority != final_priority:
            lines[start_block - 1] = lines[start_block - 1].replace(f"({existing_priority})", f"({final_priority})", 1)
        elif not existing_priority and final_priority:
            lines[start_block - 1] = f"{m.group(1)}- [{m.group(2)}] {time_str} ({final_priority}) {body}"
        block = lines[start_block - 1:end_block]
    else:
        block = create_task_block_from_title_desc_time_priority(title, desc, time=time_str, priority=final_priority, initial_spaces=m.group(1), checkbox_content=m.group(2))
        lines[start_block - 1:end_block] = block
    write_lines(path, lines)
    print(f"editada [{n}]: {lines[i - 1]}")
    for ln in block:
        print(f"  {ln}")
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def cmd_toggle(args, done):
    path = current_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args)
    if not targets:
        sys.exit("no se encontro la tarea")
    mark = "x" if done else " "
    ids = line_to_id(lines)
    for i in targets:
        m = TASK_RE.match(lines[i - 1])
        lines[i - 1] = f"{m.group(1)}- [{mark}]{m.group(3)}"
    write_lines(path, lines)
    for i in targets:
        verb = "hecha" if done else "reabierta"
        print(f"{verb} [{ids[i]}]: {lines[i - 1]}")
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)


def cmd_delete(args):
    path = current_path()
    lines = read_lines(path)
    targets, unknown = find_targets(lines, args)
    if not targets:
        sys.exit("no se encontro la tarea")
    ids = line_to_id(lines)
    blocks = task_blocks(lines)
    for i in sorted(targets, reverse=True):
        start, end = blocks[i]
        print(f"eliminada [{ids[i]}]: {lines[i - 1]}")
        for ln in lines[start:end]:
            print(f"  {ln}")
        del lines[start - 1:end]
    write_lines(path, lines)
    if unknown:
        print(f"sin coincidencias: {', '.join(unknown)}", file=sys.stderr)
        
def cmd_zoom(args):
    if not args:
        sys.exit('error: todo zoom <id1> <id2> ...')
    lines = read_lines(current_path())
    ranges = task_ranges(lines)
    for arg in args:
        try:
            arg = int(arg)
        except ValueError:
            print(f'{arg} - no encontrado')
            continue
        if arg < 1 or arg > len(ranges):
            print(f'{arg} - no encontrado')
            continue
        start, end = ranges[arg - 1]
        print("\n".join(lines[start - 1:end]))


USAGE = """todo - gestion de tareas TODO (Obsidian + git)

USO:
  todo create [-p low|mid|max] "Titulo" ["descripcion"]   crea tarea (prioridad default: low)
  todo list [--all|--done|--pending]     lista (default: pendientes)
  todo edit <id> ["p <prio>"] ["texto"]  edita texto (conserva prioridad); con `p` cambia prioridad
  todo done <id> [otros...]              marca como hecha
  todo undo <id> [otros...]              vuelve a abrir
  todo delete <id> [otros...]            elimina linea(s)
  todo zoom <id1> <id2> ...              muestra el detalle completo (sin recortar)
  todo sync ["mensaje"]                  git add -A + commit + push
  todo restore [--yes]                   descarta los cambios sin commitear del vault
  todo aim <nombre|main>                 fija el contexto: las operaciones de tareas
                                         apuntan a ese subtodo (main = el principal)
  todo sub [create|list|delete|edit]     CRUD de subtodos (.md en subTodo/); sin
                                         argumentos lista (sub list marca con [x]
                                         el activo o main)
  todo help                              este texto

ATAJOS: add == create, rm == delete, ls == list, sub rm == sub delete.

CONTEXTO (aim):
  - todo aim musica -> create/list/edit/done/undo/delete/zoom operan sobre
    subTodo/musica.md hasta que se cambie; todo aim main vuelve al principal.
  - todo aim (sin argumentos) muestra en donde estas parado.
  - El contexto se persiste en config.json (current_sub), no en el vault.
  - sub list marca con [x] el contexto activo (main si no hay ninguno).

PRIORIDADES (create -p / edit p):
  - l / low -> (low) ; m / mid / middle -> (mid) ; max / hight -> (max)
  - todo create -p mid "Titulo" [desc] ; todo edit 3 p max ["Texto"]
  - el tag (prioridad) va al inicio del titulo y el listado con colores lo
    reemplaza por color (blanco/azul/rojo), sin mostrarlo.
  - editar el texto sin `p` mantiene la prioridad actual.

DETALLES:
  - Cada tarea es una linea: - [ ] H:MM AM/PM (prioridad) Titulo: descripcion
  - [x] = hecha. El id es el ordinal de la tarea (1, 2, 3...; los
    encabezados #/## y --- no cuentan; puede cambiar al agregar/borrar).
  - done/undo/delete/edit aceptan SOLO ids numericos, nunca texto.
  - Multilinea: en PowerShell y bash los saltos de linea reales dentro de
    un argumento se guardan como continuaciones indentadas (6 espacios).
    En cmd.exe usar \n literal, ej: todo create "Titulo\\nDetalle 1\\nDetalle 2".
    todo zoom <id> muestra el bloque completo; todo delete <id> lo borra todo.
  - restore: git reset --hard HEAD en el vault (pide confirmacion; --yes la saltea).
  - sub: los subtodos son .md dentro de subTodo/ (carpeta junto al
    TODO.md principal); el gestor sub NO toca el principal.
  - Al crear el primer bloque de un archivo vacio se encabeza con un H1
    con el nombre del archivo/subtodo (sin guiones al inicio).
  - restore NO borra archivos nunca commiteados: hace todo sync primero
    para que los subtodos queden trackeados.
  - Config: .env junto al script (NOTES_ROOT, NOTES_TODO opcional).
"""
