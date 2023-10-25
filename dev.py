"""
Developer entry point.

For some _extremely odd_ reason, you must run this with the full path
to the file:

python /Users/jeff/Documents/Projects/lute_v3/dev.py

Ref https://stackoverflow.com/questions/37650208/flask-cant-find-app-file

This works on Mac:

python `pwd`/dev.py
"""

from lute.main import init_db_and_app
from lute.app_config import AppConfig

app_config = AppConfig.create_from_config()
print()
print(f'Connecting to {app_config.dbname} in folder {app_config.datapath}')
print()

app = init_db_and_app(app_config)

app.run(debug=True)
