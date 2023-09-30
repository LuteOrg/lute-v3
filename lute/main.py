"""
Main entry point
"""

import os
from flask import Flask
from lute.app_config import AppConfig
from lute.dbsetup.migrator import SqliteMigrator
from lute.dbsetup.setup import BackupManager, Setup

def _get_config():
    """
    Build config using ../config/config.yml
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    configfile = os.path.join(thisdir, '..', 'config', 'config.yml')
    return AppConfig(configfile)


def _setup_app_dirs(app_config):
    """
    App needs the data dir, backups, and other directories.
    """
    dp = app_config.datapath
    required_dirs = [
        dp,
        os.path.join(dp, 'backups')
    ]
    make_dirs = [d for d in required_dirs if not os.path.exists(d)]
    for d in make_dirs:
        os.makedirs(d)


def _create_migrator():
    """
    Create SqliteMigrator with prod migration folders.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'migrations_repeatable')
    return SqliteMigrator(migdir, repeatable)


def _setup_db(app_config):
    """
    Call setup.
    """
    dbfile = app_config.dbfilename
    backup_dir = os.path.join(app_config.datapath, 'backups')
    backup_count = 20  # Arbitrary
    bm = BackupManager(dbfile, backup_dir, backup_count)

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, 'schema', 'baseline.sql')

    migrator = _create_migrator()

    setup = Setup(dbfile, baseline, bm, migrator)
    setup.setup()


def init_db_and_app():
    """
    Main entry point.  Calls dbsetup, and returns Flask app.
    """

    app_config = _get_config()
    _setup_app_dirs(app_config)
    _setup_db(app_config)

    app = Flask(__name__)

    @app.route('/')
    def index():
        content = f"""
        <html>
        <body>
        <p>Welcome to Lute</p>
        <p>DB = {app_config.dbname}</p>
        <p>Data path = {app_config.datapath}</p>
        </body>
        </html>
        """
        return content

    return app
