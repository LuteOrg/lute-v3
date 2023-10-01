"""
Main entry point.
"""

import os
from flask import Flask
from lute.app_config import AppConfig
from lute.dbsetup.migrator import SqliteMigrator
from lute.dbsetup.setup import BackupManager, Setup

from lute.db import db

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


def _create_app(app_config):
    """
    Create the app using the given configuration,
    and init the SqlAlchemy db.
    """

    app = Flask(__name__, instance_path=app_config.datapath)

    config = {
        'SECRET_KEY': 'some_secret',
        'DATABASE': app_config.dbfilename,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{app_config.dbfilename}',

        # ref https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
        # Don't track mods.
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }

    app.config.from_mapping(config)

    db.init_app(app)

    # Blueprints to come
    # from . import auth
    # app.register_blueprint(auth.bp)

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


def init_db_and_app():
    """
    Main entry point.  Calls dbsetup, and returns Flask app.
    """

    app_config = _get_config()
    _setup_app_dirs(app_config)
    _setup_db(app_config)

    app = _create_app(app_config)

    return app
