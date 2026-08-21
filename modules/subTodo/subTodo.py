import sys

from modules.config.config import get as config_get, set_value as config_set
from modules.utils.todo import current_sub, sub_path, todo_path


class SubTodoService:
    def sub(self, args):
        if not args:
            return self._list([])
        action = args[0].lower()
        rest = args[1:]
        if action in ("create", "add"):
            self._create(rest)
        elif action in ("list", "ls"):
            self._list(rest)
        elif action in ("delete", "rm"):
            self._delete(rest)
        elif action in ("edit", "rename"):
            self._edit(rest)
        else:
            sys.exit(f"error: subcomando sub desconocido: {action}")

    def aim(self, args):
        if not args:
            name = current_sub()
            print(name if name else "main")
            return
        name = " ".join(args)
        if name in ("main", "root", "-", "."):
            config_set("current_sub", "")
            print("parado en: main")
            return
        path = sub_path(name)
        if not path.exists():
            sys.exit(f"error: no existe el subtodo: {name}")
        config_set("current_sub", name)
        print(f"parado en: {name}")

    @staticmethod
    def _validate_name(name):
        if not name:
            sys.exit("error: falta el nombre del subtodo")
        if any(c in name for c in "/\\:") or name in (".", ".."):
            sys.exit(f"error: nombre invalido: {name}")
        return name

    @staticmethod
    def _sub_path(name):
        return sub_path(name)

    def _create(self, args):
        name = self._validate_name(" ".join(args))
        path = self._sub_path(name)
        if path.exists():
            sys.exit(f"error: ya existe el subtodo: {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        print(f"subtodo creado: {path}")

    def _list(self, args):
        folder = todo_path().parent / "subTodo"
        subs = sorted(p.stem for p in folder.glob("*.md")) if folder.is_dir() else []
        active = current_sub()
        print("[x] main" if not active else "[ ] main")
        for name in subs:
            print(f"[x] {name}" if name == active else f"[ ] {name}")

    def _delete(self, args):
        name = self._validate_name(" ".join(args))
        path = self._sub_path(name)
        if not path.exists():
            sys.exit(f"error: no existe el subtodo: {name}")
        path.unlink()
        if current_sub() == name:
            config_set("current_sub", "")
        print(f"subtodo eliminado: {path.name}")

    def _edit(self, args):
        if len(args) < 2:
            sys.exit("error: `todo sub edit <nombre> <nuevo nombre>`")
        name = self._validate_name(args[0])
        new_name = self._validate_name(" ".join(args[1:]))
        old_path = self._sub_path(name)
        if not old_path.exists():
            sys.exit(f"error: no existe el subtodo: {name}")
        new_path = self._sub_path(new_name)
        if new_path.exists():
            sys.exit(f"error: ya existe el subtodo: {new_name}")
        old_path.rename(new_path)
        print(f"subtodo renombrado: {old_path.name} -> {new_path.name}")
        if current_sub() == name:
            config_set("current_sub", new_name)