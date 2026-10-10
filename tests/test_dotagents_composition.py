import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "dot_local/libexec/compose-dotagents.py"


class CompositionTests(unittest.TestCase):
    def compose(self, root):
        self.assertTrue(SCRIPT.exists(), "configuration composer has not been implemented")
        spec = importlib.util.spec_from_file_location("compose", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.compose(root)

    def test_existing_local_catalog_is_split_without_losing_private_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents.public.toml").write_text('version = 1\n[[plugins]]\nname = "public"\nsource = "path:./public"\n')
            (root / "agents.toml").write_text('version = 1\n[[plugins]]\nname = "public"\nsource = "path:./public"\n[[skills]]\nname = "private"\nsource = "path:./local"\n')
            self.compose(root)
            private = tomllib.loads((root / "agents.private.toml").read_text())
            self.assertEqual(private["plugins"], [])
            self.assertEqual(private["skills"][0]["name"], "private")
            self.assertEqual(private["skills"], tomllib.loads((root / "agents.toml").read_text())["skills"])

    def test_public_only_install_works_without_private_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents.public.toml").write_text('version = 1\nagents = ["claude"]\n[[plugins]]\nname = "public"\nsource = "path:./public"\n')
            (root / "client-state.public.json").write_text(json.dumps({"claude": {"public": {"enabled": True}}}))
            self.compose(root)
            actual = tomllib.loads((root / "agents.toml").read_text())
            self.assertEqual(actual["plugins"][0]["name"], "public")
            self.assertEqual(actual["agents"], ["claude"])

    def test_private_dependencies_and_existing_client_preferences_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents.public.toml").write_text('version = 1\nagents = ["claude"]\n[[plugins]]\nname = "public"\nsource = "path:./public"\n')
            (root / "agents.private.toml").write_text('version = 1\nagents = ["codex"]\n[[skills]]\nname = "private"\nsource = "path:./secret"\n')
            public = {"claude": {"public": {"enabled": True}}}
            local = {"claude": {"public": {"enabled": False}, "private": {"enabled": True}}}
            (root / "client-state.public.json").write_text(json.dumps(public))
            (root / "client-state.json").write_text(json.dumps(local))
            original = (root / "agents.public.toml").read_bytes()
            self.compose(root)
            actual = tomllib.loads((root / "agents.toml").read_text())
            self.assertEqual(actual["agents"], ["claude", "codex"])
            self.assertEqual(actual["skills"][0]["name"], "private")
            self.assertEqual((root / "agents.public.toml").read_bytes(), original)
            self.assertEqual(json.loads((root / "client-state.json").read_text()), local)
            self.assertEqual((root / "agents.toml").stat().st_mode & 0o777, 0o600)
            first = (root / "agents.toml").read_bytes()
            self.compose(root)
            self.assertEqual((root / "agents.toml").read_bytes(), first)

    def test_conflicting_plugin_declaration_leaves_generated_catalog_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for scope,source in [("public", "public"), ("private", "private")]:
                (root / f"agents.{scope}.toml").write_text(f'version = 1\n[[plugins]]\nname = "same"\nsource = "path:./{source}"\n')
            (root / "agents.toml").write_text("original")
            with self.assertRaisesRegex(ValueError, "Conflicting plugins"):
                self.compose(root)
            self.assertEqual((root / "agents.toml").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
