import unittest

from modules.config import config as cfg
from modules.utils import todo as utils
from tests.support import TempVaultTestCase
from todo_controller import TodoController


class RoutingTests(TempVaultTestCase):
    def setUp(self):
        super().setUp()
        cfg.set_value("active_prittier", True)

    def _lines(self):
        return utils.read_lines(utils.todo_path())

    def test_pretty_when_enabled(self):
        self.write_vault()
        out = self.run_cmd(TodoController().list, [])
        self.assertIn("\033[", out)

    def test_plain_when_disabled(self):
        self.write_vault()
        cfg.set_value("active_prittier", False)
        out = self.run_cmd(TodoController().list, [])
        self.assertNotIn("\033[", out)
        self.assertIn("- [ ] H1: integral", out)

    def test_crud_through_controller(self):
        self.write_vault()
        ctrl = TodoController()
        self.run_cmd(ctrl.create, ["Nueva", "desc"])
        self.run_cmd(ctrl.done, ["1"])
        lines = self._lines()
        self.assertEqual("- [x] H1: integral", lines[0])
        self.assertEqual("- [ ] (low) Nueva: desc", lines[-1])