import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from modules.config import config as config_mod
import modules.utils.todo as utils

SAMPLE = "- [ ] H1: integral\n- [x] Ir al gym\n\n- [ ] N8N: subir webhook\n"


class TempVaultTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._env_backup = dict(utils.ENV)
        utils.ENV["NOTES_ROOT"] = str(self.root)
        utils.ENV["NOTES_TODO"] = "TODO/TODO.md"
        self.cfg_file = self.root / "config.json"
        config_mod.CONFIG_FILE = self.cfg_file

    def tearDown(self):
        utils.ENV.clear()
        utils.ENV.update(self._env_backup)
        self.tmp.cleanup()

    def write_vault(self, content=SAMPLE):
        path = utils.todo_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_cmd(self, handler, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            handler(args)
        return buf.getvalue()