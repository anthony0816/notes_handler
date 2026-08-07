from todo import  USAGE, cmd_create, cmd_list, cmd_edit, cmd_delete, cmd_toggle
import sys
from modules.git.git import cmd_sync

def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(USAGE)
        return
    cmd, args = argv[0].lower(), argv[1:]
    if cmd == "list" or cmd == "ls":
        cmd_list(args)
    elif cmd == "create" or cmd == "add":
        cmd_create(args)
    elif cmd == "edit":
        cmd_edit(args)
    elif cmd == "done":
        cmd_toggle(args, done=True)
    elif cmd == "undo":
        cmd_toggle(args, done=False)
    elif cmd == "delete" or cmd == "rm":
        cmd_delete(args)
    elif cmd == "sync":
        cmd_sync(args)
    else:
        sys.exit(f"comando desconocido: {cmd}\n\n{USAGE}")


if __name__ == "__main__":
    main(sys.argv[1:])