import sys
import subprocess
from datetime import datetime
from modules.utils.todo import notes_root


def cmd_sync(args):
    root = notes_root()
    if not (root / ".git").exists():
        sys.exit(f"error: no es repo git: {root}")
    message = " ".join(args) or f"notas: {datetime.now():%Y-%m-%d %H:%M}"
    add = run_git(root, ["add", "-A"])
    if "error" in add.stderr.lower():
        sys.exit(f"git add fallo: {add.stderr}")
    commit = run_git(root, ["commit", "-m", message])
    if commit.returncode != 0:
        if "nothing to commit" in commit.stdout.lower():
            print("nada que commitear")
            return
        sys.exit(f"git commit fallo: {commit.stderr or commit.stdout}")
    print(commit.stdout.strip())
    push = run_git(root, ["push"])
    if push.returncode != 0:
        sys.exit(f"git push fallo: {push.stderr or push.stdout}")
    print(push.stdout.strip())
    
    
def cmd_restore(args):
    root = notes_root()
    if not (root / ".git").exists():
        sys.exit(f"error: no es repo git: {root}")
    if "--yes" not in args and "-y" not in args:
        answer = (
            input("descartar todos los cambios sin commitear del vault? (si/no): ")
            .strip()
            .lower()
        )
        if answer not in ("si", "s", "yes", "y", "1"):
            sys.exit("cancelado")
    res = run_git(root, ["reset", "--hard", "HEAD"])
    if res.returncode != 0:
        sys.exit(f"git restore fallo: {res.stderr or res.stdout}")
    print(res.stdout.strip() or "cambios descartados")


def run_git(root, args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8"
    )