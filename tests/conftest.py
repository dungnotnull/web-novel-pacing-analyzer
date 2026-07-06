"""conftest.py — make the pacing_analyzer package importable in tests."""
import os
import sys

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
