"""
User entry point.
"""

from waitress import serve
from lute.main import init_db_and_app

print('running at localhost:5000')
app = init_db_and_app()
serve(app, host="0.0.0.0", port=5000)
