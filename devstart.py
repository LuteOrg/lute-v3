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

ac = AppConfig.create_from_config()

# https://stackoverflow.com/questions/25504149/
#  why-does-running-the-flask-dev-server-run-itself-twice
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # Reloading.
    pass
else:
    # First run
    msg = f"""
    db name: {ac.dbname}
    data: {ac.datapath}

    Running at:

    http://localhost:{ac.port}

    """
    print(msg)

app = create_app(ac, output_func=print)
app.run(debug=True, port=ac.port)
