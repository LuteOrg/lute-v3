"""
User entry point.
"""

import os
import shutil
import logging
from waitress import serve
from lute.app_factory import create_app
from lute.config.app_config import AppConfig

logging.getLogger("waitress.queue").setLevel(logging.ERROR)
logging.getLogger("natto").setLevel(logging.CRITICAL)


def _print(s):
    """
    Print message to stdout.
    """
    if isinstance(s, str):
        s = s.split("\n")
    msg = "\n".join(["  " + lin.strip() for lin in s])
    print(msg, flush=True)


def _create_prod_config_if_needed():
    """
    If config.yml is missing, create one from prod config.
    """
    config_file = os.path.join(AppConfig.configdir(), "config.yml")
    if not os.path.exists(config_file):
        prod_conf = os.path.join(AppConfig.configdir(), "config.yml.prod")
        shutil.copy(prod_conf, config_file)
        _print(["", "Using new production config.", ""])


def start():
    """
    Main entry point: Get the config, init the app, and start.

    If the config file doesn't exist, use the prod config.
    """

    _print(["", "Starting Lute:", ""])

    _create_prod_config_if_needed()

    app_config = AppConfig.create_from_config()

    _print("Initializing app.")
    app = create_app(app_config, output_func=_print)
    _print(f"data path: {app_config.datapath}")
    _print(f"database: {app_config.dbfilename}")
    if app_config.is_docker:
        _print("(Note these are container paths, not host paths.)")

    port = app_config.port
    _print(
        f"""
    Running at:

    http://localhost:{port}
    """
    )

    close_msg = """
    When you're finished reading, stop this process
    with Ctrl-C or your system equivalent.
    """
    if app_config.is_docker:
        close_msg = """
        When you're finished reading, stop this container
        with Ctrl-C, docker compose stop, or docker stop <containerid>
        as appropriate.
        """
    _print(close_msg)

    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
