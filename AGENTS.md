# AGENTS.md — Guía para agentes de IA en este proyecto

CLI en Python (solo stdlib) para gestionar un vault de tareas Obsidian
versionado con git. Las tareas viven en un repo EXTERNO al proyecto; este repo
solo contiene la herramienta.

## Filosofía

1. **Markdown plano como protocolo.** Cada tarea es UNA línea:
   `- [ ] Titulo: descripcion` (`- [x]` = hecha). Obsidian y GitHub la
   renderizan; la IA la parsea con un regex.
2. **Nada de datos personales hardcodeados.** Las rutas del vault van en
   `.env` (NO trackeado) configurado desde `.env.example`. Nunca escribir
   `C:\Antonio\Notes` en el código.
3. **Cero dependencias.** Solo la librería estándar de Python. No instalar
   paquetes sin permiso explícito.
4. **Código sin comentarios.** Nada de comentarios en el código; la
   documentación va en README.md, AGENTS.md y el USAGE del CLI.
5. **Reutilización antes que duplicación.** Toda lógica compartida va en
   `modules/utils/` y se importa, nunca se copia.

## Estructura del proyecto

| Ruta | Qué vive ahí |
| --- | --- |
| `todo_main.py` | Entrypoint. Solo el dispatch de comandos CLI hacia el `TodoController`. |
| `todo_controller.py` | `TodoController`: orquesta los comandos; decide entre `todo.py` y `prittier` según `config` para `list`. |
| `todo.py` | Comandos CRUD (`cmd_create`, `cmd_list`, `cmd_edit`, `cmd_toggle`, `cmd_delete`) + `USAGE`. NO tocar su lógica para integrar features nuevas. |
| `modules/utils/todo.py` | Helpers compartidas: `notes_root`, `todo_path`, `read_lines`, `write_lines`, `parse_task`, `todo_items`, `filter_task`, `mode_from_args`, constantes `TASK_RE`, `DEFAULT_TODO_REL`, `ENV`. |
| `modules/env/env.py` | Carga del `.env` (`load_env`). |
| `modules/config/config.py` | Preferencias activables/desactivables (`config.json`, gitignored): schema, `load`, `get`, `set_value`, `cmd_config`. |
| `modules/prittier/prittier.py` | Listado con colores (`pretty_print_list`) + soporte ANSI en Windows. |
| `modules/git/git.py` | Operaciones git (`cmd_sync`). |
| `todo.cmd` / `todo.sh` | Wrappers Windows/bash que llaman a `todo_main.py`. |
| `skill/todo-notes/SKILL.md` | Skill de opencode que viaja en el repo; copiar a `~/.config/opencode/skills/` para activarla. |
| `.env.example` | Plantilla de config del vault (`.env` real no se versiona). |

## Dónde va cada cosa

- **Nuevo comando CLI** → función `cmd_*` en `todo.py` + método en
  `TodoController` + registro en `todo_main.py` + entrada en `USAGE` y en la skill.
- **Lógica reutilizable** (parseo, rutas, I/O de archivos) → `modules/utils/todo.py`.
- **Feature de presentación/UI** de un comando existente (ej. listado bonito) →
  módulo propio (`modules/prittier/`) y el `TodoController` decide según
  config; NO tocar la lógica CRUD de `todo.py`.
- **Preferencias activables** → `modules/config/config.py` (schema + persistencia
  en `config.json`).
- **Algo específico de git** → `modules/git/git.py`.
- **Algo específico de config/env** → `modules/env/env.py`.

## Convenciones

- Las rutas se resuelven SIEMPRE via `notes_root()` / `todo_path()` de
  `modules.utils.todo`, nunca hardcodeadas.
- `ENV` se carga una vez en `modules/utils/todo.py` al importar; no recargar
  `.env` en otros módulos.
- Los archivos de tareas se leen/escriben con `read_lines` / `write_lines`
  (siempre UTF-8, normalizan con `\n` final).
- Los ids de tareas son números de línea; si una operación agrega/borra
  líneas, los ids posteriores cambian (así está documentado, no "arreglarlo").

## Verificación

```console
python -m py_compile todo.py todo_main.py todo_controller.py modules/env/env.py modules/git/git.py modules/utils/todo.py
python todo_main.py list
```

`todo_main.py sync` hace `git add -A` + commit + push sobre el repo del vault
(externo). OJO: toca git de verdad (pide confirmación al usuario si no la hay).

## Prohibido

- Tocar el `.env` del usuario (es personal).
- Commitear/pushear del vault sin que el usuario lo pida.
- Cambiar el formato de las tareas (`- [ ]` / `- [x]`) sin acordarlo.
