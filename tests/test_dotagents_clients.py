import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "dot_local/libexec/register-dotagents.py"


class ClientTests(unittest.TestCase):
    def test_repeated_install_preserves_a_plugin_disabled_after_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / ".agents").mkdir()
            (home / ".claude").mkdir()
            state = {"claude": {"example": {"legacy": "example@old", "enabled": True}}}
            (home / ".agents/client-state.json").write_text(json.dumps(state))
            (home / ".claude/settings.json").write_text(json.dumps({"enabledPlugins": {"example@dotagents": False}}))
            spec = importlib.util.spec_from_file_location("clients", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.register(home, options_only=True)
            module.register(home)
            settings = json.loads((home / ".claude/settings.json").read_text())
            self.assertFalse(settings["enabledPlugins"]["example@dotagents"])

    def test_preserves_native_settings_and_moves_plugin_options_and_disabled_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / ".agents").mkdir()
            (home / ".claude").mkdir()
            (home / ".codex").mkdir()
            state = {"claude": {"example": {"legacy": "example@old", "enabled": True},
                                   "disabled": {"legacy": "disabled@old", "enabled": False}},
                     "codex": {"example": {"legacy": "example@old", "enabled": True}}}
            (home / ".agents/client-state.json").write_text(json.dumps(state))
            settings = {"model": "my-model", "hooks": {"Notification": []},
                        "enabledPlugins": {"example@old": True, "unrelated@host": True},
                        "pluginConfigs": {"example@old": {"options": {"SECRET": "local-only"}}}}
            (home / ".claude/settings.json").write_text(json.dumps(settings))
            (home / ".codex/config.toml").write_text(
                'model = "my-model"\n[mcp_servers.native]\ncommand = "native"\n'
                'cwd = "/native/path"\n[plugins."example@old"]\nenabled = true\n'
                '[[skills.config]]\npath = "' + str(home / '.codex/skills/example/SKILL.md') + '"\nenabled = false\n')
            self.assertTrue(SCRIPT.exists(), "client migration has not been implemented")
            spec = importlib.util.spec_from_file_location("clients", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.register(home)
            actual = json.loads((home / ".claude/settings.json").read_text())
            self.assertEqual(actual["model"], "my-model")
            self.assertEqual(actual["hooks"], {"Notification": []})
            self.assertTrue(actual["enabledPlugins"]["unrelated@host"])
            self.assertFalse(actual["enabledPlugins"]["example@old"])
            self.assertTrue(actual["enabledPlugins"]["example@dotagents"])
            self.assertFalse(actual["enabledPlugins"]["disabled@dotagents"])
            self.assertEqual(actual["pluginConfigs"]["example@dotagents"]["options"]["SECRET"], "local-only")
            codex = tomllib.loads((home / ".codex/config.toml").read_text())
            self.assertEqual(codex["mcp_servers"]["native"]["cwd"], "/native/path")
            self.assertFalse(codex["plugins"]["example@old"]["enabled"])
            self.assertTrue(codex["plugins"]["example@dotagents-local"]["enabled"])
            self.assertEqual(codex["skills"]["config"][0]["path"], str(home / ".agents/skills/example/SKILL.md"))
            first = (home / ".codex/config.toml").read_text()
            module.register(home)
            self.assertEqual((home / ".codex/config.toml").read_text(), first)


if __name__ == "__main__":
    unittest.main()
