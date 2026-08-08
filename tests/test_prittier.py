import unittest

from modules.prittier.prittier import pretty_print_list
from tests.support import TempVaultTestCase


class PrtTests(TempVaultTestCase):
    def test_pretty_all_includes_colors_and_titles(self):
        self.write_vault()
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("\033[", out)
        self.assertIn("H1: integral", out)
        self.assertIn("Ir al gym", out)

    def test_pending_filters_done(self):
        self.write_vault()
        out = self.run_cmd(pretty_print_list, [])
        self.assertIn("H1: integral", out)
        self.assertNotIn("Ir al gym", out)

    def test_done_mode(self):
        self.write_vault()
        out = self.run_cmd(pretty_print_list, ["--done"])
        self.assertIn("Ir al gym", out)
        self.assertNotIn("H1: integral", out)

    def test_empty_vault(self):
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("sin tareas", out)

    def test_full_text_no_clip_on_narrow(self):
        self.write_vault("- [ ] A very long title that should survive entirely\n")
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("A very long title that should survive entirely", out)