"""
Main entry point.
"""

import os
from flask import Flask, render_template
from lute.dbsetup.migrator import SqliteMigrator
from lute.dbsetup.setup import BackupManager, Setup

from lute.db import db

from . import language


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


def _create_app(app_config, extra_config):
    """
    Create the app using the given configuration,
    and init the SqlAlchemy db.
    """

    app = Flask(__name__, instance_path=app_config.datapath)

    config = {
        'SECRET_KEY': 'some_secret',
        'DATABASE': app_config.dbfilename,
        'ENV': app_config.env,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{app_config.dbfilename}',

        # ref https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
        # Don't track mods.
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }

    final_config = { **config, **extra_config }
    app.config.from_mapping(final_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(language.bp)

    @app.route('/')
    def index():
        return render_template(
            'index.html',
            dbname = app_config.dbname,
            datapath = app_config.datapath
        )

    return app


def init_db_and_app(app_config, extra_config = None):
    """
    Main entry point.  Calls dbsetup, and returns Flask app.

    Use extra_config to pass { 'TESTING': True } during unit tests.
    """

    _setup_app_dirs(app_config)
    _setup_db(app_config)

    if extra_config is None:
        extra_config = {}
    app = _create_app(app_config, extra_config)

    return app
