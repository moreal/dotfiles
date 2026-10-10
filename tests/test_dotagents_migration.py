import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "dot_local/libexec/prepare-dotagents.py"


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def write(self, relative, content):
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def migrate(self):
        self.assertTrue(SCRIPT.exists(), "migration helper has not been implemented")
        spec = importlib.util.spec_from_file_location("migration", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.prepare(self.home)

    def test_merges_metadata_and_keeps_system_and_cloud_managed_skills(self):
        self.write(".agents/skill-sources/example/SKILL.md", "skill")
        self.write(".codex/skills/example/SKILL.md", "skill")
        self.write(".codex/skills/example/agents/openai.yaml", "metadata")
        self.write(".codex/skills/.system/tool/SKILL.md", "system")
        self.write(".claude/skills/example/SKILL.md", "skill")
        self.write(".claude/skills/synced/account/example/SKILL.md", "cloud")
        self.write(".agents/skills/other/SKILL.md", "other")
        backup = self.migrate()
        self.assertEqual((self.home / ".agents/skills/example/agents/openai.yaml").read_text(), "metadata")
        self.assertEqual((self.home / ".agents/skills/other/SKILL.md").read_text(), "other")
        self.assertTrue((self.home / ".claude/skills").is_symlink())
        self.assertEqual((self.home / ".claude/skills/synced/account/example/SKILL.md").read_text(), "cloud")
        self.assertTrue((self.home / ".codex/skills/.system/tool/SKILL.md").exists())
        self.assertFalse((self.home / ".codex/skills/example").exists())
        self.assertEqual((backup / ".codex/skills/example/SKILL.md").read_text(), "skill")
        self.assertEqual(self.migrate(), backup)

    def test_conflicting_files_abort_before_moving_any_originals(self):
        self.write(".agents/skill-sources/example/SKILL.md", "source")
        self.write(".agents/skills/example/SKILL.md", "source")
        original = self.write(".claude/skills/example/SKILL.md", "local edit")
        with self.assertRaisesRegex(ValueError, "Conflicting skill"):
            self.migrate()
        self.assertEqual(original.read_text(), "local edit")
        self.assertFalse((self.home / ".agents/.migration-complete.json").exists())

    def test_preserves_live_repository_skill_links_in_backup(self):
        self.write(".agents/skill-sources/review/SKILL.md", "review")
        target = self.write("repo/skills/review/SKILL.md", "review").parent
        link = self.home / ".codex/skills/review"
        link.parent.mkdir(parents=True)
        link.symlink_to(target, target_is_directory=True)
        backup = self.migrate()
        self.assertTrue((backup / ".codex/skills/review").is_symlink())
        self.assertEqual((self.home / ".agents/skills/review/SKILL.md").read_text(), "review")


if __name__ == "__main__":
    unittest.main()
