import json
import unittest

from modules.config import config as cfg
from tests.support import TempVaultTestCase


class ConfigTests(TempVaultTestCase):
    def test_defaults_without_file(self):
        self.assertFalse(self.cfg_file.exists())
        self.assertTrue(cfg.get("active_prittier"))

    def test_set_and_get(self):
        cfg.set_value("active_prittier", False)
        self.assertFalse(cfg.get("active_prittier"))
        self.assertTrue(self.cfg_file.exists())

    def test_bool_aliases(self):
        for raw in ("SI", "on", "1", "true", "yes"):
            cfg.set_value("active_prittier", raw)
            self.assertTrue(cfg.get("active_prittier"))
        for raw in ("no", "off", "0", "false"):
            cfg.set_value("active_prittier", raw)
            self.assertFalse(cfg.get("active_prittier"))

    def test_invalid_bool_exits(self):
        with self.assertRaises(SystemExit):
            cfg.set_value("active_prittier", "quizas")

    def test_unknown_key_exits(self):
        with self.assertRaises(SystemExit):
            cfg.set_value("nueva", True)

    def test_save_drops_phantom_keys(self):
        self.cfg_file.write_text(
            '{"active_prittier": true, "fantasma": 1}\n', encoding="utf-8"
        )
        cfg.set_value("active_prittier", False)
        data = json.loads(self.cfg_file.read_text(encoding="utf-8"))
        self.assertEqual({"active_prittier": False}, data)

    def test_load_ignores_phantom_keys(self):
        self.cfg_file.write_text('{"fantasma": true}\n', encoding="utf-8")
        self.assertTrue(cfg.get("active_prittier"))

    def test_list_cmd(self):
        out = self.run_cmd(cfg.cmd_config, ["list"])
        self.assertIn("active_prittier", out)

    def test_set_cmd_prints(self):
        out = self.run_cmd(cfg.cmd_config, ["set", "active_prittier", "false"])
        self.assertIn("False", out)