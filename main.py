"""
User entry point.
"""

from waitress import serve
from lute.main import init_db_and_app
from lute.app_config import AppConfig

app_config = AppConfig.create_from_config()
app = init_db_and_app(app_config)

port = app_config.port
print(f'running at localhost:{port}')
serve(app, host="0.0.0.0", port=port)
