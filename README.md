# todo — Gestión de tareas TODO (Obsidian + git)

CLI en Python para gestionar tus tareas en un vault Obsidian versionado con
git. Las tareas viven en `TODO.md` como markdown plano, así que las editas
tanto desde el CLI, desde Obsidian o desde cualquier editor.

## Cómo funciona

- El repo de notas está en `C:\Antonio\Notes` (remoto: `github.com/anthony0816/NOTES`).
- El archivo de tareas es `C:\Antonio\Notes\TODO\TODO\TODO.md`.
- Cada tarea es una línea:
  ```
  - [ ] Título: descripción corta
  ```
- `- [ ]` = pendiente · `- [x]` = hecha.
- El **id** de una tarea es su número de línea en el archivo (puede cambiar al editar).

## Instalación

Python 3.12+ (solo usa la librería estándar, sin dependencias). Clonar o copiar
este proyecto y copiar la config:

```console
copy .env.example .env
```

Luego configurar la ruta en `.env`:

```
NOTES_ROOT=C:\Antonio\Notes
```

`NOTES_ROOT` es obligatoria (el CLI falla con un error claro si no está).
Opcionalmente `NOTES_TODO` (por defecto `TODO/TODO/TODO.md`, relativo al vault).
También se pueden sobreescribir con variables de entorno del sistema.
`.env` está en `.gitignore`; solo se versiona `.env.example`.

## Comandos

```console
todo create "Título" ["descripción"]   crea una tarea
todo list [--all|--done|--pending]     lista tareas (default: pendientes)
todo edit <id> "nuevo texto"           cambia título/descripción
todo done <id|texto> [otras...]        marca como hecha (- [x])
todo undo <id|texto> [otras...]        vuelve a abrir (- [ ])
todo delete <id|texto> [otras...]      elimina la línea
todo sync ["mensaje"]                  git add -A + commit + push
todo help                              muestra esta ayuda
```

Atajos: `add` = `create`, `ls` = `list`, `rm` = `delete`.

Los ids aceptan también búsqueda por texto parcial. Releé con `todo list`
después de cada operación porque los números de línea pueden cambiar.

## Agregar `todo` al PATH (Windows)

Para poder ejecutar `todo` desde cualquier terminal sin escribir la ruta
completa (`C:\Antonio\Python\Proyectos\notes_handler\todo.cmd`):

1. En el buscador de Windows, escribí **"Variables de entorno"** y abrí
   *Editar las variables de entorno del sistema*.
2. Clic en **Variables de entorno…**.
3. En *Variables de usuario* seleccioná **Path** y clic en **Editar…**.
4. **Nuevo** y pegá la ruta del proyecto:
   ```
   C:\Antonio\Python\Proyectos\notes_handler
   ```
5. Aceptá todo y **abrí una terminal nueva** (el PATH ya cargado no se actualiza).

Por las instrucciones, se ejecuta `todo.cmd` que llama a `python todo.py`.

## Uso con agentes de IA (opencode)

La skill `todo-notes` documenta este protocolo y viaja en el repo en
`skill/todo-notes/SKILL.md`. Para que tu agente la use, copiala (o apuntá
`skills.paths`) a `.opencode/skills/todo-notes/` dentro del proyecto o a
`~\.config\opencode\skills\todo-notes\`. Con ella podés decirle a un agente
"agregá tal tarea" y él usa `todo create / done / list / sync` solo.

## Ejemplo rápido

```console
> todo create "Comprar pan" "integral, 500g"
creada [3]: - [ ] Comprar pan: integral, 500g
> todo done 3
hecha [3]: - [x] Comprar pan: integral, 500g
> todo sync
[master 509ca7f] notas: 2026-08-06 16:40
```