---
name: todo-notes
description: Gestiona el vault TODO del usuario (tareas en Obsidian/markdown versionado con git). Usar cuando el usuario pida crear, listar, editar, completar, reabrir, eliminar o sincronizar tareas/todos, o mencionar "mis notas", "todo", "TODO.md", "todo list", "todo create", "todo sync". Requiere ejecutar comandos de todo.py.
---

# TODO Notes

El usuario gestiona sus notas en un vault Obsidian versionado con git en
`C:\Antonio\Notes` (repo remoto: github.com/anthony0816/NOTES).

El archivo de tareas es `C:\Antonio\Notes\TODO\TODO\TODO.md`.

Las rutas del vault se configuran en `.env` (NOTES_ROOT obligatoria,
NOTES_TODO opcional, default `TODO/TODO.md`); ver README.md.

## Protocolo de tareas

Cada tarea es UNA linea de markdown:

```
- [ ] Titulo: descripcion corta
```

- `- [ ]` = pendiente, `- [x]` = hecha.
- Título obligatorio; descripción opcional separada con `: `.
- El ID de una tarea es su numero de linea en el archivo (1-indexado).
- No inventar otros formatos; respetar las lineas existentes.

## Comandos

Todos se ejecutan como `python todo.py <comando>` o `todo <comando>`, desde el
directorio del proyecto (donde esta `todo.py`).

| Comando | Efecto |
| --- | --- |
| `todo create [-p low\|mid\|max] "Titulo" ["desc"]` | crea tarea al final del archivo con prioridad (default `low`) |
| `todo list [--all\|--done\|--pending]` | lista tareas (default: pendientes) con su id |
| `todo edit <id> ["p <prio>"] ["texto"]` | edita texto (conserva prioridad); con `p` cambia la prioridad |
| `todo done <id o texto>` | marca como hecha (`- [x]`) |
| `todo undo <id o texto>` | vuelve a abrir (`- [ ]`) |
| `todo delete <id o texto>` | elimina la linea |
| `todo zoom <id> [mas ids...]` | muestra el detalle completo de la tarea (sin recortar) |
| `todo sync ["mensaje"]` | `git add -A` + commit + push del repo completo |
| `todo config list\|get\|set` | preferencias (ej. `active_prittier` para colores) |
| `todo help` | ayuda |

Atajos: `add` = `create`, `rm` = `delete`, `ls` = `list`.

Prioridades: `-p`/`p` acepta `low, l`, `m, mid, middle`, `max, hight` (tag
`(prio)` al inicio del titulo). Editar texto sin `p` conserva la prioridad.

`todo list` delega en el módulo `prittier` (colores) si la config
`active_prittier` está activa; si no, usa el listado plano.

Los argumentos de `done`/`undo`/`delete` aceptan ids numericos o texto parcial
a buscar. Se pueden pasar varios a la vez. Despues de cada operacion los ids
pueden cambiar: releer con `todo list` antes de operar.

## Instalación de la skill

Para que un agente de opencode la use, copiarla (o apuntar skills.paths) a:

- Proyecto: `.opencode/skills/todo-notes/SKILL.md`
- Global: `~/.config/opencode/skills/todo-notes/SKILL.md`

## Uso desde el agente

1. Para agregar una tarea: `todo create "<titulo>" "<desc>"`.
2. Para marcar hecha una tarea que el usuario nombra: `todo list`, ubicar el
   id y `todo done <id>`. Si no se encuentra, crear con `create`.
3. Para cambiar el texto de una tarea: `todo edit <id> "nuevo texto"`.
4. Para ver el detalle completo de una tarea recortada en el listado:
   `todo zoom <id>`.
5. Cuando el usuario pida guardar/actualizar todo: `todo sync`.
6. No editar TODO.md a mano salvo caso excepcional; siempre via `todo.py`.