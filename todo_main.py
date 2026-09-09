import sys

from todo import USAGE
from todo_controller import TodoController
from modules.subTodo.subTodo import SubTodoService


def main(argv):
        
    todo = TodoController()
    subTodo = SubTodoService()
    if len(argv) == 0:
         argv = ['ls']
    cmd, args = argv[0].lower(), argv[1:]
    handlers = {
        "list": todo.list,
        "ls": todo.list,
        "create": todo.create,
        "add": todo.create,
        "edit": todo.edit,
        "done": todo.done,
        "undo": todo.undo,
        "delete": todo.delete,
        "rm": todo.delete,
        "sync": todo.sync,
        "restore": todo.restore,
        "config": todo.config,
        "zoom" : todo.zoom,
        "sub": subTodo.sub,
        "aim": subTodo.aim
    }
    handler = handlers.get(cmd)

    if not argv or argv[0] in ("help", "-h", "--help"):
            print(USAGE)
            return

    if handler:
        handler(args)
    else:
        sys.exit(f"comando desconocido: {cmd}\n\n{USAGE}")


if __name__ == "__main__":
    main(sys.argv[1:])