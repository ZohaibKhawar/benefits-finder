"""Entry point for PythonAnywhere (or any WSGI host): it imports the Flask app as `application`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app as application  # noqa: E402
