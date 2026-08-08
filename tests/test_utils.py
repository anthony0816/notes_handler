import unittest
from pathlib import Path

import modules.utils.todo as utils
from tests.support import TempVaultTestCase


class ParseTaskTests(unittest.TestCase):
    def test_pending(self):
        done, indent, text = utils.parse_task("- [ ] Hacer pan: integral")
        self.assertFalse(done)
        self.assertEqual("", indent)
        self.assertEqual("Hacer pan: integral", text)

    def test_done_lower(self):
        done, _, _ = utils.parse_task("- [x] hecho")
        self.assertTrue(done)

    def test_done_upper(self):
        done, _, _ = utils.parse_task("- [X] hecho")
        self.assertTrue(done)

    def test_indent(self):
        done, indent, text = utils.parse_task("  - [ ] ind")
        self.assertFalse(done)
        self.assertEqual("  ", indent)
        self.assertEqual("ind", text)

    def test_no_match(self):
        self.assertIsNone(utils.parse_task("- Hacer pan"))
        self.assertIsNone(utils.parse_task(""))
        self.assertIsNone(utils.parse_task("texto suelto"))


class SplitTaskTextTests(unittest.TestCase):
    def test_with_desc(self):
        self.assertEqual(("Titulo", "desc"), utils.split_task_text("Titulo: desc"))

    def test_without_desc(self):
        self.assertEqual(("Solo  titulo", ""), utils.split_task_text("  Solo  titulo  "))

    def test_colon_in_desc(self):
        self.assertEqual(("T", "a: b"), utils.split_task_text("T: a: b"))


class FilterTaskTests(unittest.TestCase):
    def test_all(self):
        self.assertTrue(utils.filter_task(True, "all"))
        self.assertTrue(utils.filter_task(False, "all"))

    def test_done(self):
        self.assertTrue(utils.filter_task(True, "done"))
        self.assertFalse(utils.filter_task(False, "done"))

    def test_pending(self):
        self.assertTrue(utils.filter_task(False, "pending"))
        self.assertFalse(utils.filter_task(True, "pending"))


class ModeFromArgsTests(unittest.TestCase):
    def test_default(self):
        self.assertEqual("pending", utils.mode_from_args([]))

    def test_all(self):
        self.assertEqual("all", utils.mode_from_args(["--all"]))
        self.assertEqual("all", utils.mode_from_args(["-a"]))

    def test_done(self):
        self.assertEqual("done", utils.mode_from_args(["--done"]))
        self.assertEqual("done", utils.mode_from_args(["-d"]))


class ReadWriteLinesTests(TempVaultTestCase):
    def test_missing_file(self):
        self.assertEqual([], utils.read_lines(utils.todo_path()))

    def test_roundtrip(self):
        utils.write_lines(utils.todo_path(), ["a", "b"])
        self.assertEqual(["a", "b"], utils.read_lines(utils.todo_path()))

    def test_normalizes_trailing_newline(self):
        path = utils.todo_path()
        utils.write_lines(path, ["a"])
        self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))


class PathResolutionTests(TempVaultTestCase):
    def test_relative(self):
        utils.ENV["NOTES_TODO"] = "a/b.md"
        self.assertEqual(self.root / "a" / "b.md", utils.todo_path())

    def test_absolute(self):
        utils.ENV["NOTES_TODO"] = str(self.root / "X" / "t.md")
        self.assertEqual(Path(self.root / "X" / "t.md"), utils.todo_path())

    def test_default_rel(self):
        utils.ENV.pop("NOTES_TODO", None)
        self.assertEqual(self.root / utils.DEFAULT_TODO_REL, utils.todo_path())

    def test_points_to_temp(self):
        self.assertNotEqual(Path(str(utils.notes_root())), Path("C:/Antonio/Notes"))


class TodoItemsTests(TempVaultTestCase):
    def test_items(self):
        self.write_vault()
        items = utils.todo_items()
        self.assertEqual([1, 2, 4], [it["id"] for it in items])
        self.assertEqual([False, True, False], [it["done"] for it in items])
        self.assertEqual("H1: integral", items[0]["text"])
        self.assertEqual("N8N: subir webhook", items[2]["text"])