import os
import shutil
import sys

from modules.utils.todo import (
    UNKNOWN_SEGMENT,
    filter_task,
    mode_from_args,
    parse_segments,
    read_lines,
    segment_title,
    split_priority,
    todo_items,
    todo_path,
)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
STRIKE = "\033[9m"
RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[94m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"

STATE_W = 7
MODE_LABEL = {"all": "todas", "done": "hechas", "pending": "pendientes"}

PRIORITY_COLOR = {"low": WHITE, "mid": BLUE, "max": RED}


def enable_ansi():
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        ctable = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(ctable)):
            kernel32.SetConsoleMode(handle, ctable.value | 0x0004)


def _text_width(items, full=False):
    cols = shutil.get_terminal_size().columns
    max_w = max(20, cols - 22)
    longest = max((len(it["text"]) for it in items), default=20)
    if full:
        return longest
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
        visible = "[ ] pend"
        color = YELLOW
    return f"{BOLD}{color}{visible:<{STATE_W}}{RESET}"


def _cell_text(item, width):
    priority, rest = split_priority(item["text"])
    color = PRIORITY_COLOR[priority] if priority else WHITE
    bold = BOLD if not item["done"] and priority in ("mid", "max") else ""
    body = _clip(rest, width)
    if item["done"]:
        return f"{DIM}{color}{STRIKE}{body}{RESET}"
    return f"{bold}{color}{body}{RESET}"


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
    segments = parse_segments(read_lines(todo_path()))
    for seg in segments:
        seg_items = [it for it in items if it["id"] in seg["task_idx"]]
        if not seg_items:
            continue
        if seg["date"] and seg["date"].strip() != UNKNOWN_SEGMENT:
            title = segment_title(seg["date"])
            total = text_width + 15
            dashes = max(0, total - len(title))
            left = dashes // 2
            right = dashes - left
            print(
                f"{DIM}{'-' * left}{RESET}"
                f"{BOLD}{CYAN}{title}{RESET}"
                f"{DIM}{'-' * right}{RESET}"
            )
        for it in seg_items:
            print(f" {_cell_state(it)}  {_cell_id(it)}  {_cell_text(it, text_width)}")
    _summary(all_items)
    
def pretty_zoom_tasks(args):
    if not args:
        sys.exit('error: todo zoom <id1> <id2> ...')
    all_items =  todo_items()
    for  arg in args :
        arg = int(arg)
        if arg < 1 or arg > len(all_items):
            print(f'{arg} - no encontrado')
            continue
        item =  all_items[arg - 1]
        
        print(f" {_cell_state(item)}  {_cell_id(item)}  {_cell_text(item, _text_width([item], full=True))}")
    