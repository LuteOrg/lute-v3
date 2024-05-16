"""
Developer entry point.  Runs lute on a dev server.

This script _always_ uses the config at /lute/config/config.yml.

You can run with:

inv start
python -m devstart

If you want to run this with "python", then for some _extremely odd_
reason, you must run this with the full path to the file.
Ref https://stackoverflow.com/questions/37650208/flask-cant-find-app-file

e.g.:

python /Users/jeff/Documents/Projects/lute_v3/devstart.py
python `pwd`/devstart.py
"""

import os
import argparse
import logging
from lute.app_factory import create_app
from lute.config.app_config import AppConfig

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


def start(port):
    """
    Start the dev server with reloads on port.
    """

    def dev_print(s):
        "Print info on first load only."
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            # https://stackoverflow.com/questions/25504149/
            #  why-does-running-the-flask-dev-server-run-itself-twice
            # Reloading, do nothing.
            return
        print(s)

    config_file = AppConfig.default_config_filename()
    dev_print("")
    app = create_app(config_file, output_func=dev_print)

    ac = AppConfig(config_file)
    dev_print(f"\ndb name: {ac.dbname}")
    dev_print(f"data: {ac.datapath}")
    dev_print(f"Running at: http://localhost:{port}\n")

    app.run(debug=True, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start dev server lute.")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port number (default: 5000)"
    )
    args = parser.parse_args()
    start(args.port)
