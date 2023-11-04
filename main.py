"""
User entry point.
"""

import logging
from waitress import serve
from lute.app_setup import init_db_and_app
from lute.config.app_config import AppConfig

logging.getLogger("waitress.queue").setLevel(logging.ERROR)

app_config = AppConfig.create_from_config()
app = init_db_and_app(app_config)

port = app_config.port
print(f'running at localhost:{port}')
serve(app, host="0.0.0.0", port=port)
