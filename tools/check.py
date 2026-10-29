"""check.py: the one-command check the pre-commit hook runs (pytest suite; text lint joins it once script/ exists)."""
import subprocess
import sys

sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "tests"]))
