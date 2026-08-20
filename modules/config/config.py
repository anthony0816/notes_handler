import json
import sys
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.json"

SCHEMA = {
    "active_prittier": {
        "default": True,
        "type": "bool",
        "description": "Muestra el listado con colores (prittier).",
    },
    "current_sub": {
        "default": "",
        "type": "string",
        "description": "Subtodo activo para las operaciones de tareas (\"\" = TODO.md principal).",
    },
}


def _coerce(value, entry):
    if entry["type"] == "bool":
        if isinstance(value, bool):
            return value
        low = str(value).strip().lower()
        if low in ("true", "1", "yes", "on", "si"):
            return True
        if low in ("false", "0", "no", "off"):
            return False
        raise ValueError(f"valor invalido para bool: {value}")
    return str(value)


def load():
    cfg = {k: v["default"] for k, v in SCHEMA.items()}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
        for key, entry in SCHEMA.items():
            if key in data:
                try:
                    cfg[key] = _coerce(data[key], entry)
                except ValueError:
                    pass
    return cfg


def save(cfg):
    clean = {k: cfg[k] for k in SCHEMA if k in cfg}
    CONFIG_FILE.write_text(
        json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def get(key):
    return load().get(key, SCHEMA[key]["default"])


def set_value(key, value):
    if key not in SCHEMA:
        sys.exit(
            f"error: config desconocida: {key}. "
            "No se pueden crear ni eliminar configs; solo editar las existentes."
        )
    try:
        parsed = _coerce(value, SCHEMA[key])
    except ValueError as exc:
        sys.exit(f"error: {exc}")
    cfg = load()
    cfg[key] = parsed
    save(cfg)
    return parsed


def cmd_config(args):
    if not args:
        sys.exit("error: usa `todo config list` o `todo config set <clave> <valor>`")
    sub = args[0]
    if sub in ("list", "ls"):
        for key, entry in SCHEMA.items():
            cfg = load()
            print(f"{key} = {cfg[key]}  [{entry['type']}] {entry['description']}")
    elif sub == "set":
        if len(args) < 3:
            sys.exit("error: `todo config set <clave> <valor>`")
        value = set_value(args[1], args[2])
        print(f"config {args[1]} = {value}")
    elif sub == "get":
        if len(args) < 2:
            sys.exit("error: `todo config get <clave>`")
        print(get(args[1]))
    else:
        sys.exit(f"error: subcomando config desconocido: {sub}")