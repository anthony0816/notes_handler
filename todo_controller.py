from modules.config.config import cmd_config, get as config_get
from modules.git.git import cmd_sync
from modules.prittier.prittier import pretty_print_list, pretty_zoom_tasks
from todo import cmd_create, cmd_delete, cmd_edit, cmd_list, cmd_toggle, cmd_zoom


class TodoController:
    def list(self, args):
        if config_get("active_prittier"):
            pretty_print_list(args)
        else:
            cmd_list(args)

    def create(self, args):
        cmd_create(args)

    def edit(self, args):
        cmd_edit(args)

    def done(self, args):
        cmd_toggle(args, done=True)

    def undo(self, args):
        cmd_toggle(args, done=False)

    def delete(self, args):
        cmd_delete(args)

    def sync(self, args):
        cmd_sync(args)

    def config(self, args):
        cmd_config(args)
    
    def zoom(self, args):
        if config_get("active_prittier"):
            pretty_zoom_tasks(args)
        else:
            cmd_zoom(args)