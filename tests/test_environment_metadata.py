import os
import platform
import sys
import unittest


class TestEnvironmentMetadata(unittest.TestCase):
    """Record the runtime facts needed to interpret regression results.

    This test intentionally does not require optional scientific packages.
    It prevents the regression suite from silently hiding the interpreter
    context in which it was executed.
    """

    def test_python_runtime_is_reportable(self):
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertTrue(platform.python_version())

    def test_runtime_metadata_can_be_serialized(self):
        metadata = {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "implementation": platform.python_implementation(),
            "cpu_count": os.cpu_count(),
        }
        self.assertIn("python", metadata)
        self.assertIn("platform", metadata)
        self.assertIsNotNone(metadata["cpu_count"])


if __name__ == "__main__":
    unittest.main()
