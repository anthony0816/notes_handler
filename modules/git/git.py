import  sys 
from datetime import datetime
from todo import notes_root
import subprocess


def cmd_sync(args):
    root = notes_root()
    if not (root / ".git").exists():
        sys.exit(f"error: no es repo git: {root}")
    message = " ".join(args) or f"notas: {datetime.datetime.now():%Y-%m-%d %H:%M}"
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
    
    
def run_git(root, args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8"
    )