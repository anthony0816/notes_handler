import os
import shutil

from modules.utils.todo import filter_task, mode_from_args, todo_items

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
STRIKE = "\033[9m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"

STATE_W = 13
MODE_LABEL = {"all": "todas", "done": "hechas", "pending": "pendientes"}


def enable_ansi():
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        ctable = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(ctable)):
            kernel32.SetConsoleMode(handle, ctable.value | 0x0004)


def _text_width(items):
    cols = shutil.get_terminal_size().columns
    max_w = max(20, cols - 22)
    longest = max((len(it["text"]) for it in items), default=20)
    return min(max(longest, 20), max_w)


def _clip(text, width):
    shown = " ".join(text.split())
    if len(shown) <= width:
        return shown
    return shown[: width - 3] + "..."


def _cell_id(item):
    color = GREEN if item["done"] else WHITE
    return f"{BOLD}{color}{item['id']:>4}{RESET}"


def _cell_state(item):
    if item["done"]:
        visible = "[x] done"
        color = GREEN
    else:
        visible = "[ ] pending"
        color = YELLOW
    return f"{BOLD}{color}{visible:<{STATE_W}}{RESET}"


def _cell_text(item, width):
    body = _clip(item["text"], width)
    if item["done"]:
        return f"{DIM}{GREEN}{STRIKE}{body}{RESET}"
    return f"{WHITE}{body}{RESET}"


def _print_header(text_width):
    width = 4 + 2 + STATE_W + 2 + text_width
    print(f"{BOLD}{CYAN}{'STATE':<{STATE_W}}{RESET}  {BOLD}{CYAN}{'ID':>4}{RESET}  {BOLD}{CYAN}TASK{RESET}")
    print(f"{DIM}{CYAN}{'-' * width}{RESET}")


def _summary(all_items):
    total = len(all_items)
    done = sum(1 for it in all_items if it["done"])
    pending = total - done
    if not total:
        return
    print(f"{DIM}{'-' * 4}{RESET}")
    label_done = GREEN if done else DIM
    label_pend = YELLOW if pending else DIM
    print(
        f"{BOLD}{MAGENTA}{total}{RESET} tasks | "
        f"{label_done}{done} done tasks{RESET} | "
        f"{label_pend}{pending} pending tasks{RESET}"
    )


def pretty_print_list(args):
    enable_ansi()
    mode = mode_from_args(args)
    all_items = todo_items()
    items = [it for it in all_items if filter_task(it["done"], mode)]
    if not items:
        print(f"{DIM}(sin tareas {MODE_LABEL[mode]}){RESET}")
        return
    text_width = _text_width(items)
    _print_header(text_width)
    for it in items:
        print(f" {_cell_state(it)}  {_cell_id(it)}  {_cell_text(it, text_width)}")
    _summary(all_items)