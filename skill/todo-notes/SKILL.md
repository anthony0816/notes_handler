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
- El ID es el ordinal de la tarea (1, 2, 3...): solo cuentan las lineas
  `- [ ]`/`- [x]`; los encabezados `#`/`##`, `---` y lineas en blanco no
  computan.
- No inventar otros formatos; respetar las lineas existentes.

## Comandos

Todos se ejecutan como `python todo.py <comando>` o `todo <comando>`, desde el
directorio del proyecto (donde esta `todo.py`).

| Comando | Efecto |
| --- | --- |
| `todo create [-p low\|mid\|max] "Titulo" ["desc"]` | crea tarea en el bloque del dia de hoy (lo crea si no existe) con prioridad (default `low`) |
| `todo list [--all\|--done\|--pending]` | lista tareas (default: pendientes) con su id |
| `todo edit <id> ["p <prio>"] ["texto"]` | edita texto (conserva prioridad); con `p` cambia la prioridad |
| `todo done <id>` | marca como hecha (`- [x]`) |
| `todo undo <id>` | vuelve a abrir (`- [ ]`) |
| `todo delete <id>` | elimina la linea |
| `todo zoom <id> [mas ids...]` | muestra el detalle completo de la tarea (sin recortar) |
| `todo sync ["mensaje"]` | `git add -A` + commit + push del repo completo |
| `todo restore [--yes]` | descarta los cambios sin commitear del vault (`git reset --hard`); no toca archivos sin trackear |
| `todo aim <nombre\|main>` | fija el contexto: las operaciones de tareas apuntan a ese subtodo (main = principal); sin argumentos muestra dónde estás |
| `todo sub [create\|list\|delete\|edit]` | CRUD de subtodos (`.md` en `subTodo/`, junto al TODO.md, NO toca el principal); sin argumentos lista, marcando con `[x]` el contexto activo o `main` |
| `todo config list\|get\|set` | preferencias (ej. `active_prittier` para colores, `current_sub` para el contexto) |
| `todo help` | ayuda |

Atajos: `add` = `create`, `rm` = `delete`, `ls` = `list`.

Prioridades: `-p`/`p` acepta `low, l`, `m, mid, middle`, `max, hight` (tag
`(prio)` al inicio del titulo). Editar texto sin `p` conserva la prioridad.

`todo list` delega en el módulo `prittier` (colores) si la config
`active_prittier` está activa; si no, usa el listado plano.

Los argumentos de `done`/`undo`/`delete`/`edit` aceptan SOLO ids numericos,
nunca texto parcial (evita alterar tareas por substring). Se pueden pasar
varios ids a la vez. El id es el ordinal de la tarea (1, 2, 3...; los
encabezados #/## y --- no cuentan). Despues de cada operacion los ids pueden
cambiar: releer con `todo list` antes de operar.

El contexto (`current_sub`) se persiste en `config.json`. Si el usuario crea
tareas en un subtodo, `todo list` sin más ya las muestra: conviene revisar
`todo aim` y `todo sub` para saber dónde está parado antes de operar. Los
subtodos nuevos no están trackeados por git hasta el próximo `todo sync`.

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