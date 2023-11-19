"""
User entry point.

Start lute running on given port, or 5000 if not set.

e.g.

python -m lute.main --port 5001
"""

import os
import argparse
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


def _create_app(config_file_path=None):
    """
    Configure and init the app.

    Uses config file if set (throws if doesn't exist);
    otherwise, uses the prod config, creating a prod config
    if necessary.
    """
    _print(["", "Starting Lute:"])

    if config_file_path is not None:
        _print([f"Using specified config: {config_file_path}"])
    elif os.path.exists("config.yml"):
        _print(["Using config.yml found in root"])
        config_file_path = "config.yml"
    else:
        _print(["Using default config"])
        _create_prod_config_if_needed()
        config_file_path = AppConfig.default_config_filename()

    app_config = AppConfig(config_file_path)

    _print(["", "Initializing app."])
    app = create_app(config_file_path, output_func=_print)
    _print(f"data path: {app_config.datapath}")
    _print(f"database: {app_config.dbfilename}")
    if app_config.is_docker:
        _print("(Note these are container paths, not host paths.)")

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

    return app


def _start(args):
    "Configure and start the app."
    app = _create_app(args.config)

    _print(
        f"""
    Lute is running.  Open a web browser, and go to:

    http://localhost:{args.port}
    """
    )
    serve(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start lute.")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port number (default: 5000)"
    )
    parser.add_argument(
        "--config",
        help="Path to override config file.  Uses lute/config/config.yml if not set.",
    )
    try:
        _start(parser.parse_args())
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("\n")
        print("-" * 50)
        print("Error during startup:")
        print(e)
        print("Please try again, or report an issue on GitHub.")
        print("-" * 50)
