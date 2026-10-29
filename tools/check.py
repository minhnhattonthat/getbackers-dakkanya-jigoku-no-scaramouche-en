"""check.py: the one-command check the pre-commit hook runs (pytest suite, incl. the script/ lint in tests/test_script.py)."""
import subprocess
import sys

sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "tests"]))
