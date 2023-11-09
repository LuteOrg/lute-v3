"""
Copy of main.py, running the server on port 9876.

This still connects to the test database etc.
"""

import sys
import logging
from waitress import serve

if len(sys.argv) != 2:
    raise RuntimeError("have to pass port arg.")

# Hack the path, or python can't find the lute package when this is run
# from the root dir using "python -m this.module.name"
#
# pylint: disable=wrong-import-position
sys.path.append("..")
from lute.app_factory import create_app
from lute.config.app_config import AppConfig

logging.getLogger("waitress.queue").setLevel(logging.ERROR)

app_config = AppConfig.create_from_config()
app = create_app(app_config)

port = int(sys.argv[1])
print(f"running at localhost:{port}")
serve(app, host="0.0.0.0", port=port)
