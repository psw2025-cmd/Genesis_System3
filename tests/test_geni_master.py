"""
Tests for System3 GENI Master Agent

Tests import checks, path correctness, state management, and orchestrator.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestGeniImports(unittest.TestCase):
    """Test that all GENI modules can be imported."""

    def test_import_geni_config(self):
        """Test geni_config import."""
        from core.geni import geni_config

        self.assertIsNotNone(geni_config.PROJECT_ROOT)
        self.assertTrue(geni_config.PROJECT_ROOT.exists())

    def test_import_geni_state(self):
        """Test geni_state import."""
        from core.geni import geni_state

        self.assertIsNotNone(geni_state.GeniState)

    def test_import_geni_tasks(self):
        """Test geni_tasks import."""
        from core.geni import geni_tasks

        self.assertIsNotNone(geni_tasks.get_all_tasks)

    def test_import_geni_validator(self):
        """Test geni_validator import."""
        from core.geni import geni_validator

        self.assertIsNotNone(geni_validator.run_full_validation)

    def test_import_geni_orchestrator(self):
        """Test geni_orchestrator import."""
        from core.geni import geni_orchestrator

        self.assertIsNotNone(geni_orchestrator.run_geni_master)


class TestGeniPaths(unittest.TestCase):
    """Test path correctness."""

    def test_project_root_exists(self):
        """Test that PROJECT_ROOT exists and contains system3_ultra.py."""
        from core.geni.geni_config import PROJECT_ROOT, SYSTEM3_ULTRA_ENTRY

        self.assertTrue(PROJECT_ROOT.exists())
        self.assertTrue(SYSTEM3_ULTRA_ENTRY.exists())

    def test_storage_path_exists(self):
        """Test that PATH_STORAGE exists."""
        from core.geni.geni_config import PATH_STORAGE

        self.assertTrue(PATH_STORAGE.exists())


class TestGeniState(unittest.TestCase):
    """Test state read/write."""

    def setUp(self):
        """Set up test with temporary state file."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_file = self.temp_dir / "test_state.json"

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_state_write_read(self):
        """Test writing and reading state."""
        from core.geni.geni_state import GeniState, load_state, save_state

        # Create state
        state = GeniState.default()
        state.env_ok = True
        state.validation_passed = True

        # Save
        save_state(state, self.state_file)
        self.assertTrue(self.state_file.exists())

        # Load
        loaded_state = load_state(self.state_file)
        self.assertEqual(loaded_state.env_ok, True)
        self.assertEqual(loaded_state.validation_passed, True)

    def test_state_default(self):
        """Test default state creation."""
        from core.geni.geni_state import GeniState

        state = GeniState.default()
        self.assertIsNotNone(state.timestamp)
        self.assertFalse(state.env_ok)
        self.assertFalse(state.validation_passed)


class TestGeniOrchestrator(unittest.TestCase):
    """Test orchestrator dry-run."""

    def test_status_mode(self):
        """Test status mode (light check only)."""
        from core.geni.geni_orchestrator import run_geni_master

        # This should not fail, even if validation scripts don't exist
        # It should return 0 or 1, but not crash
        try:
            exit_code = run_geni_master("status")
            self.assertIn(exit_code, [0, 1])
        except Exception as e:
            self.fail(f"Status mode should not crash: {e}")

    def test_last_run_files_created(self):
        """Test that last run files are created."""
        from core.geni.geni_config import GENI_LAST_RUN_JSON, GENI_LAST_RUN_MD
        from core.geni.geni_orchestrator import run_geni_master

        # Run status mode
        run_geni_master("status")

        # Check files exist
        self.assertTrue(GENI_LAST_RUN_JSON.exists())
        self.assertTrue(GENI_LAST_RUN_MD.exists())

        # Check JSON is valid
        with GENI_LAST_RUN_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIn("timestamp", data)
            self.assertIn("mode", data)


class TestGeniTasks(unittest.TestCase):
    """Test task registry."""

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        from core.geni.geni_tasks import get_all_tasks

        tasks = get_all_tasks()
        self.assertGreater(len(tasks), 0)
        self.assertIn("full_validation", tasks)

    def test_get_task(self):
        """Test getting specific task."""
        from core.geni.geni_tasks import get_task

        task = get_task("full_validation")
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "full_validation")


if __name__ == "__main__":
    # Use unittest instead of pytest
    unittest.main(verbosity=2)
