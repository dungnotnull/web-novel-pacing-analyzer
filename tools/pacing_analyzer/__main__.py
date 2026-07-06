"""__main__.py — allow `python -m pacing_analyzer ...` execution."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
