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
- Opcionalmente, al inicio del título va un tag de prioridad:
  ```
  - [ ] (max) Título: descripción corta
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
Opcionalmente `NOTES_TODO` (por defecto `TODO/TODO.md`, relativo al vault).
`.env` está en `.gitignore`; solo se versiona `.env.example`.

## Comandos

```console
todo create [-p <prioridad>] "Título" ["descripción"]   crea una tarea
todo list [--all|--done|--pending]     lista tareas (default: pendientes)
todo edit <id> <"p <prioridad>"> ["nuevo título"]   edita texto/prioridad
todo done <id|texto> [otras...]        marca como hecha (- [x])
todo undo <id|texto> [otras...]        vuelve a abrir (- [ ])
todo delete <id|texto> [otras...]      elimina la línea
todo zoom <id> [más ids...]            muestra la tarea con su detalle completo (sin recortar)
todo sync ["mensaje"]                  git add -A + commit + push
todo restore [--yes]                   descarta los cambios sin commitear del vault
todo check <nombre|main>               fija el contexto: las operaciones de tareas
                                       apuntan a ese subtodo (main = el principal)
todo sub [create|list|delete|edit]     CRUD de subtodos; sin argumentos lista
todo help                              muestra esta ayuda
```

Atajos: `add` = `create`, `ls` = `list`, `rm` = `delete` (también en `todo sub`).

Los ids aceptan también búsqueda por texto parcial. Releé con `todo list`
después de cada operación porque los números de línea pueden cambiar.

### Subtodos (`todo sub`)

Un subtodo es simplemente un `.md` (con el nombre que se decida) que vive en
una carpeta `subTodo/` en el **mismo directorio que el TODO.md principal**
(ej. `Todo/SubTodo/musica.md` en el vault). Sirve para llevar listas paralelas
(`todo sub create musica`) sin tocar el archivo principal:

```console
todo sub create musica              crea musica.md
todo sub                            lista los subtodos (o `todo sub list`)
todo sub edit musica "musica 2026"  renombra el archivo
todo sub delete musica              lo elimina
```

`todo sub list` marca con `[x]` el contexto activo (`main` si no hay ninguno):

```console
[ ] main
[x] musica
[ ] lectura
```

El gestor `sub` **nunca toca el TODO.md principal**; solo crea/lista/
renombra/borra sus propios `.md` dentro de `subTodo/`. Los nombres no admiten
`/`, `\` ni `:`.

### Pararse en un subtodo (`todo check`)

`todo check <nombre>` fija un contexto: desde ese momento, todos los comandos
de tareas (`create`, `list`, `done`, `undo`, `edit`, `delete`, `zoom`) operan
sobre ese subtodo, sin escribir flags en cada comando:

```console
todo check musica        me paro en musica (ya debe existir)
todo create "comprar vinilos"     -> va a subTodo/musica.md
todo list                -> lista musica.md
todo check main          vuelvo al TODO.md principal
todo check               muestra en dónde estoy parado (main o el subtodo)
```

El contexto se persiste en `config.json` (clave `current_sub`), no en el
vault, y al crear el primer bloque de un archivo vacío se encabeza con un H1
con el nombre del archivo (ej. `# musica`).

### Restaurar cambios (`todo restore`)

Si algo quedó a medio tocar en el vault (tareas sin commitear o editadas por
error), `todo restore` descarta **todos los cambios sin commitear** del repo
(`git reset --hard HEAD`). Pide confirmación; se saltea con `--yes`. Los
archivos **sin trackear no se tocan**: para que un subtodo nuevo entre bajo
control de git, hacé `todo sync` (que hace `git add -A`) antes de depender de
`restore` para revertirlo.

### Zoom: ver el detalle completo de una tarea

El listado recorta los textos largos con `...` para ajustarse al ancho de la
terminal. `todo zoom` muestra la tarea con su texto **íntegro**, sin recortar:

```console
> todo zoom 3 7
```

Se pueden pasar varios ids a la vez. Si algún id no existe, avisa
`N - no encontrado` y sigue con los demás. Con el listado de colores activo
(`active_prittier`), el detalle se muestra con el formato de la prioridad
(color, negrita y estado); en modo plano se muestra la línea tal cual está en
el archivo (incluido el tag `(prioridad)`).

## Prioridades

Al crear una tarea se guarda un tag de prioridad al inicio del título:
`(low)`, `(mid)` o `(max)`.

```console
> todo create "Comprar pan"                              -> - [ ] (low) Comprar pan
> todo create -p mid "Reunión" "con el equipo"           -> - [ ] (mid) Reunión: con el equipo
> todo create -p max "Publicar release"                  -> - [ ] (max) Publicar release
```

Sin `-p` la prioridad es `low`. Con `-p` se aceptan estas etiquetas:

| Etiquetas | Prioridad guardada |
| --- | --- |
| `low`, `l` | `(low)` |
| `m`, `mid`, `middle` | `(mid)` |
| `max`, `hight` | `(max)` |

### Editar prioridad de una tarea existente

`todo edit` acepta el mismo flag `p` para cambiar la prioridad, con opción de
editar también el texto:

```console
> todo edit 3 p max                          # solo cambia la prioridad
> todo edit 3 p mid "Nuevo título"           # prioridad + título/desc
> todo edit 3 "Nuevo título"                 # edita texto, MANTIENE la prioridad actual
```

Igual que `create`, acepta `-p` o `p` y las etiquetas de la tabla. Si editás el
texto sin `p`, el tag de prioridad existente se conserva (no se pierde).

En el listado con colores (`prittier`) el tag **no se muestra**: se reemplaza
por el color de la prioridad. `low` en blanco, `mid` en azul brillante y `max`
en rojo brillante (negrita). Las completadas mantienen el color de su prioridad
pero se ven opacas y tachadas, así se distingue a la vez el estado y la
prioridad.

## Configuración

Preferencias activables/desactivables en `config.json` (no se versiona):

```console
todo config list                        lista las configs y su valor
todo config get active_prittier        consulta una config
todo config set active_prittier true   activa el listado con colores
```

La config del listado hoy es:

| Clave | Tipo | Descripción |
| --- | --- | --- |
| `active_prittier` | bool | Muestra `todo list` con colores (módulo `prittier`). Sin él, usa el listado plano. |

El dispatch lo decide `todo_main.py`: si `active_prittier` está activo, el
comando `list` delega en `modules/prittier/`; si no, en `todo.py`.

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

Por las instrucciones, se ejecuta `todo.cmd` que llama a `python todo_main.py`.

## Uso con agentes de IA (opencode)

La skill `todo-notes` documenta este protocolo y viaja en el repo en
`skill/todo-notes/SKILL.md`. Para que tu agente la use, copiala (o apuntá
`skills.paths`) a `.opencode/skills/todo-notes/` dentro del proyecto o a
`~\.config\opencode\skills\todo-notes\`. Con ella podés decirle a un agente
"agregá tal tarea" y él usa `todo create / done / list / sync` solo.

## Ejemplo rápido

```console
> todo create "Comprar pan" "integral, 500g"
creada [3]: - [ ] (low) Comprar pan: integral, 500g
> todo create -p max "Publicar release"
creada [4]: - [ ] (max) Publicar release
> todo done 3
hecha [3]: - [x] (low) Comprar pan: integral, 500g
> todo sync
[master 509ca7f] notas: 2026-08-06 16:40
```