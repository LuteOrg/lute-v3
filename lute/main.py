"""
User entry point.
"""

import logging
from waitress import serve
from lute.app_setup import init_db_and_app
from lute.config.app_config import AppConfig

logging.getLogger("waitress.queue").setLevel(logging.ERROR)


def start():
    app_config = AppConfig.create_from_config()
    app = init_db_and_app(app_config)

    port = app_config.port
    msg = f"""
    Starting Lute:
      data path: {app_config.datapath}
      database: {app_config.dbfilename}
    """

    if app_config.is_docker:
        msg += """
    Lute is in a Docker container,
    ensure data path is mounted to the host!
        """

    msg += f"""
    Running at localhost:{port} ...
    """

    print(msg)
    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
