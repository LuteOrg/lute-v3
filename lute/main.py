"""
User entry point.
"""

import os
import shutil
import logging
from waitress import serve
from lute.app_setup import init_db_and_app
from lute.config.app_config import AppConfig

logging.getLogger("waitress.queue").setLevel(logging.ERROR)
logging.getLogger('natto').setLevel(logging.CRITICAL)


def start():
    """
    Main entry point: Get the config, init the app, and start.

    If the config file doesn't exist, use the prod config.
    """

    def _print(s):
        msg = "\n".join([
            '  ' + lin.strip()
            for lin in s.split("\n")
        ])
        print(msg, flush=True)

    _print(['', 'Starting Lute:', ''])

    config_file = os.path.join(AppConfig.configdir(), 'config.yml')
    if not os.path.exists(config_file):
        prod_conf = os.path.join(AppConfig.configdir(), 'config.yml.prod')
        shutil.copy(prod_conf, config_file)
        _print(['', 'Using new production config.', ''])

    app_config = AppConfig.create_from_config()
    app = init_db_and_app(app_config, output_func = _print)

    port = app_config.port
    _print([f"data path: {app_config.datapath}",
            f"database: {app_config.dbfilename}"])

    if app_config.is_docker:
        _print([
            '',
            'Lute is in a Docker container,',
            'ensure data path is mounted to the host!'
            ''])

    _print(['',
            'Running at:',
            '',
            f'http://localhost:{port}',
            '',
            "When you're finished reading, stop this process",
            'with Ctrl-C or your system equivalent.',
            ''])

    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
