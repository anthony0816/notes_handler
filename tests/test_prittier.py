import unittest

from modules.prittier.prittier import _cell_text, pretty_print_list
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

    def test_mid_priority_renders_blue_and_strips_tag(self):
        self.write_vault("- [ ] (mid) Reunion\n")
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("\033[94m", out)
        self.assertIn("\033[1m\033[94m", out)
        self.assertNotIn("(mid)", out)
        self.assertIn("Reunion", out)

    def test_max_priority_renders_red_and_strips_tag(self):
        self.write_vault("- [ ] (max) Urgente\n")
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("\033[91m", out)
        self.assertIn("\033[1m\033[91m", out)
        self.assertNotIn("(max)", out)
        self.assertIn("Urgente", out)

    def test_low_priority_renders_white(self):
        self.write_vault("- [ ] (low) Rutina\n")
        out = self.run_cmd(pretty_print_list, ["--all"])
        self.assertIn("\033[97m", out)
        self.assertNotIn("(low)", out)
        self.assertIn("Rutina", out)
        cell = _cell_text({"done": False, "text": "(low) Rutina"}, 50)
        self.assertNotIn("\033[1m", cell)

    def test_no_priority_defaults_white(self):
        self.run_cmd(pretty_print_list, ["--all"])
        item = {"done": False, "text": "Normal"}
        out = _cell_text(item, 50)
        self.assertIn("\033[97m", out)
        self.assertNotIn("(low)", out)

    def test_done_uses_priority_color_dim_strike(self):
        item = {"done": True, "text": "(max) Hecha"}
        out = _cell_text(item, 50)
        self.assertIn("\033[2m\033[91m\033[9m", out)
        self.assertNotIn("\033[32m", out)
        self.assertNotIn("(max)", out)
        self.assertIn("Hecha", out)