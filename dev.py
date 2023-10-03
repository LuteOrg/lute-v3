"""
Developer entry point.

For some _extremely odd_ reason, you must run this with the full path
to the file:

python /Users/jeff/Documents/Projects/lute_v3/dev.py

Ref https://stackoverflow.com/questions/37650208/flask-cant-find-app-file

This works on Mac:

python `pwd`/dev.py
"""

import os
from lute.main import init_db_and_app
from lute.app_config import AppConfig

thisdir = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(thisdir, 'config', 'config.yml')
app_config = AppConfig(configfile)
app = init_db_and_app(app_config)

app.run(debug=True)
