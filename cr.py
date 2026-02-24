"""
DSA Complexity Runner – one-line loader
Usage (first cell of any notebook):

    # NO_ANALYZE
    import cr

That's it. No path setup needed.
"""
import sys

# ── Force-reload so edits to complexity_runner.py are always picked up ────────
for _mod in list(sys.modules.keys()):
    if "complexity_runner" in _mod or _mod == "utils":
        del sys.modules[_mod]

# ── Activate ──────────────────────────────────────────────────────────────────
from utils.complexity_runner import setup_complexity_runner
setup_complexity_runner()
