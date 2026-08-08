import unittest

import modules.utils.todo as utils
from tests.support import TempVaultTestCase
from todo import cmd_create, cmd_delete, cmd_edit, cmd_toggle


class CreateTests(TempVaultTestCase):
    def test_creates_pending_line(self):
        self.write_vault()
        out = self.run_cmd(cmd_create, ["Nueva", "con detalle"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual("- [ ] Nueva: con detalle", lines[-1])
        self.assertIn("creada", out)

    def test_without_desc(self):
        self.write_vault()
        self.run_cmd(cmd_create, ["Sola"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual("- [ ] Sola", lines[-1])

    def test_requires_title(self):
        self.write_vault()
        with self.assertRaises(SystemExit):
            self.run_cmd(cmd_create, [])


class EditTests(TempVaultTestCase):
    def test_edit_by_id_keeps_status(self):
        self.write_vault()
        self.run_cmd(cmd_edit, ["1", "H1: nuevo"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual("- [ ] H1: nuevo", lines[0])

    def test_edit_by_text_keeps_done(self):
        self.write_vault()
        self.run_cmd(cmd_edit, ["gym", "Correr"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual("- [x] Correr", lines[1])

    def test_edit_unknown_exits(self):
        self.write_vault()
        with self.assertRaises(SystemExit):
            self.run_cmd(cmd_edit, ["zzz", "nada"])

    def test_edit_requires_text(self):
        self.write_vault()
        with self.assertRaises(SystemExit):
            self.run_cmd(cmd_edit, ["1"])


class ToggleTests(TempVaultTestCase):
    def test_done(self):
        self.write_vault()
        self.run_cmd(lambda a: cmd_toggle(a, done=True), ["1"])
        lines = utils.read_lines(utils.todo_path())
        self.assertTrue(lines[0].startswith("- [x]"))

    def test_undo(self):
        self.write_vault()
        self.run_cmd(lambda a: cmd_toggle(a, done=False), ["gym"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual("- [ ] Ir al gym", lines[1].replace("  ", " "))

    def test_toggle_unknown_exits(self):
        self.write_vault()
        with self.assertRaises(SystemExit):
            self.run_cmd(lambda a: cmd_toggle(a, done=True), ["999"])


class DeleteTests(TempVaultTestCase):
    def test_delete_by_id(self):
        self.write_vault()
        self.run_cmd(cmd_delete, ["1"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual(["- [x] Ir al gym", "", "- [ ] N8N: subir webhook"], lines)

    def test_delete_by_text(self):
        self.write_vault()
        self.run_cmd(cmd_delete, ["gym"])
        lines = utils.read_lines(utils.todo_path())
        self.assertEqual(["- [ ] H1: integral", "", "- [ ] N8N: subir webhook"], lines)

    def test_delete_unknown_exits(self):
        self.write_vault()
        with self.assertRaises(SystemExit):
            self.run_cmd(cmd_delete, ["999"])