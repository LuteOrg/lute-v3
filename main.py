"""
User entry point.
"""

import os
from waitress import serve
from lute.main import init_db_and_app
from lute.app_config import AppConfig

thisdir = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(thisdir, 'config', 'config.yml')
app_config = AppConfig(configfile)
app = init_db_and_app(app_config)

port = app_config.port
print(f'running at localhost:{port}')
serve(app, host="0.0.0.0", port=port)
