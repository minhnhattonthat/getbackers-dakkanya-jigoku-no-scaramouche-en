"""check.py: the one-command check the pre-commit hook runs (pytest suite, incl. the script/ lint in tests/test_script.py)."""
import subprocess
import sys

# no faulthandler: unicorn (tests/test_vwf.py) raises a handled Windows access violation that it would print as a crash
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:faulthandler", "tests"]))
