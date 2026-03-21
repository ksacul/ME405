import sys
from pathlib import Path
import time as _time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

project = "ME405"
author = "Lucas Kaemmerer, Brandon Petty"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]

autodoc_mock_imports = [
    "pyb",
    "micropython",
    "utime",
    "serial",
    "matplotlib",
]

# Patch a few MicroPython-style names that your modules may import from time
if not hasattr(_time, "ticks_us"):
    _time.ticks_us = lambda: 0

if not hasattr(_time, "sleep_ms"):
    _time.sleep_ms = lambda ms: None

templates_path = ["_templates"]
exclude_patterns = []
html_theme = "alabaster"
html_static_path = ["_static"]
