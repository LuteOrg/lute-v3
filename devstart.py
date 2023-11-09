"""
Developer entry point.  Runs lute on a dev server.

You can run with:

inv devstart
python -m devstart

If you want to run this with "python", then for some _extremely odd_
reason, you must run this with the full path to the file.
Ref https://stackoverflow.com/questions/37650208/flask-cant-find-app-file

e.g.:

python /Users/jeff/Documents/Projects/lute_v3/devstart.py
python `pwd`/devstart.py
"""

import os
import logging
from lute.app_factory import create_app
from lute.config.app_config import AppConfig

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

app_config = AppConfig.create_from_config()

# https://stackoverflow.com/questions/25504149/
#  why-does-running-the-flask-dev-server-run-itself-twice
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    # First run
    print()
    print(
        f"Connecting to {app_config.dbname} in folder {app_config.datapath}", flush=True
    )
    print()
else:
    # Reloading.
    pass

app = create_app(app_config, output_func=print)
app.run(debug=True, port=app_config.port)
