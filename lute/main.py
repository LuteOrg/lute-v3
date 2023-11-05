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


def start():
    """
    Main entry point: Get the config, init the app, and start.

    If the config file doesn't exist, use the prod config.
    """

    msg = """
    Starting Lute:
    """

    config_file = os.path.join(AppConfig.configdir(), 'config.yml')
    if not os.path.exists(config_file):
        prod_conf = os.path.join(AppConfig.configdir(), 'config.yml.prod')
        shutil.copy(prod_conf, config_file)
        msg += """
          Using new production config.
        """

    app_config = AppConfig.create_from_config()
    app = init_db_and_app(app_config)

    port = app_config.port
    msg += f"""
      data path: {app_config.datapath}
      database: {app_config.dbfilename}
    """

    if app_config.is_docker:
        msg += """
    Lute is in a Docker container,
    ensure data path is mounted to the host!
        """

    msg += f"""
    Running at:

    http://localhost:{port}

    When you're finished reading, stop this process
    with Ctrl-C or your system equivalent.
    """

    msg = "\n".join([
        '  ' + lin.strip()
        for lin in msg.split("\n")
    ])

    print(msg)
    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
