"""
Factory.

Methods: create_app.
"""

import os
import json
import platform
import traceback
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    current_app,
    make_response,
    send_from_directory,
    jsonify,
)
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool

from lute.config.app_config import AppConfig
from lute.db import db
from lute.db.setup.main import setup_db
from lute.db.data_cleanup import clean_data
import lute.backup.service as backupservice
import lute.db.demo
import lute.utils.formutils

from lute.parse.registry import init_parser_plugins, supported_parsers

from lute.models.book import Book
from lute.models.language import Language
from lute.models.setting import BackupSettings, UserSetting
from lute.book.stats import refresh_stats, mark_stale

from lute.book.routes import bp as book_bp
from lute.language.routes import bp as language_bp
from lute.term.routes import bp as term_bp
from lute.termtag.routes import bp as termtag_bp
from lute.read.routes import bp as read_bp
from lute.bing.routes import bp as bing_bp
from lute.userimage.routes import bp as userimage_bp
from lute.useraudio.routes import bp as useraudio_bp
from lute.termimport.routes import bp as termimport_bp
from lute.backup.routes import bp as backup_bp
from lute.dev_api.routes import bp as dev_api_bp
from lute.settings.routes import bp as settings_bp
from lute.themes.routes import bp as themes_bp
from lute.stats.routes import bp as stats_bp
from lute.cli.commands import bp as cli_bp


def _setup_app_dirs(app_config):
    """
    App needs the data dir, backups, and other directories.
    """
    dp = app_config.datapath
    required_dirs = [
        {"d": dp, "readme": "Lute data folder."},
        {
            "d": app_config.default_user_backup_path,
            "readme": "Default path for user backups, can be overridden in settings.",
        },
        {
            "d": app_config.system_backup_path,
            "readme": "Database backups created by Lute at app start, just in case.",
        },
        {
            "d": app_config.userimagespath,
            "readme": "User images.  Each subfolder is a language's ID.",
        },
        {
            "d": app_config.userthemespath,
            "readme": "User themes.  <theme_name>.css files for your personal themes.",
        },
        {
            "d": app_config.useraudiopath,
            "readme": "User audio.  Each file is a book's audio.",
        },
        {
            "d": app_config.temppath,
            "readme": "Temp directory for export file writes, to avoid permissions issues.",
        },
    ]
    for rec in required_dirs:
        d = rec["d"]
        if not os.path.exists(d):
            os.makedirs(d)
        readme = os.path.join(d, "README.md")
        if not os.path.exists(readme):
            with open(readme, "w", encoding="utf-8") as f:
                f.write(rec["readme"])


def _add_base_routes(app, app_config):
    """
    Add some basic routes.
    """

    @app.context_processor
    def inject_menu_bar_vars():
        """
        Inject backup settings into the all templates for the menu bar.
        """
        bs = BackupSettings.get_backup_settings()
        have_languages = len(db.session.query(Language).all()) > 0
        ret = {
            "have_languages": have_languages,
            "backup_enabled": bs.backup_enabled,
            "backup_directory": bs.backup_dir,
            "backup_last_display_date": bs.last_backup_display_date,
            "backup_time_since": bs.time_since_last_backup,
            "user_settings": json.dumps(UserSetting.all_settings()),
        }
        return ret

    @app.route("/")
    def index():
        is_production = not lute.db.demo.contains_demo_data()
        bkp_settings = BackupSettings.get_backup_settings()

        have_books = len(db.session.query(Book).all()) > 0
        have_languages = len(db.session.query(Language).all()) > 0
        language_choices = lute.utils.formutils.language_choices("(all languages)")
        current_language_id = lute.utils.formutils.valid_current_language_id()

        should_run_auto_backup = backupservice.should_run_auto_backup(bkp_settings)
        # Only back up if we have books, otherwise the backup is
        # kicked off when the user empties the demo database.
        if is_production and have_books and should_run_auto_backup:
            return redirect("/backup/backup", 302)

        refresh_stats()
        warning_msg = backupservice.backup_warning(bkp_settings)
        backup_show_warning = (
            bkp_settings.backup_warn
            and bkp_settings.backup_enabled
            and warning_msg != ""
        )

        return render_template(
            "index.html",
            hide_homelink=True,
            dbname=app_config.dbname,
            datapath=app_config.datapath,
            tutorial_book_id=lute.db.demo.tutorial_book_id(),
            have_books=have_books,
            have_languages=have_languages,
            language_choices=language_choices,
            current_language_id=current_language_id,
            is_production_data=is_production,
            # Backup stats
            backup_show_warning=backup_show_warning,
            backup_warning_msg=warning_msg,
        )

    @app.route("/refresh_all_stats")
    def refresh_all_stats():
        books_to_update = db.session.query(Book).filter(Book.archived == 0).all()

        for book in books_to_update:
            mark_stale(book)

        refresh_stats()

        return redirect("/", 302)

    @app.route("/wipe_database")
    def wipe_db():
        if lute.db.demo.contains_demo_data():
            lute.db.demo.delete_demo_data()
            msg = """
            The database has been wiped clean.  Have fun! <br /><br />
            <i>(Lute has automatically enabled backups --
            change your <a href="/settings/index">Settings</a> as needed.)</i>
            """
            flash(msg)
        return redirect("/", 302)

    @app.route("/remove_demo_flag")
    def remove_demo():
        if lute.db.demo.contains_demo_data():
            lute.db.demo.remove_flag()
            msg = """
            Demo mode deactivated. Have fun! <br /><br />
            <i>(Lute has automatically enabled backups --
            change your <a href="/settings/index">Settings</a> as needed.)</i>
                        """
            flash(msg)
        return redirect("/", 302)

    @app.route("/version")
    def show_version():
        ac = current_app.env_config
        return render_template(
            "version.html",
            version=lute.__version__,
            datapath=ac.datapath,
            database=ac.dbfilename,
            is_docker=ac.is_docker,
        )

    @app.route("/hotkeys")
    def show_hotkeys():
        return render_template("hotkeys.html")

    @app.route("/info")
    def show_info():
        """
        Json return of some data.

        Used in lute.verify module for tests.

        This likely belongs in a different 'api' location,
        but leaving it here for now.
        """
        ret = {
            "version": lute.__version__,
            "datapath": current_app.config["DATAPATH"],
            "database": current_app.config["DATABASE"],
        }
        return jsonify(ret)

    @app.route("/static/js/never_cache/<path:filename>")
    def custom_js(filename):
        """
        Some files should never be cached.
        """
        response = make_response(send_from_directory("static/js", filename))
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

    @app.errorhandler(500)
    def _internal_server_error(e):  # pylint: disable=unused-argument
        """
        Custom error handler for 500 Internal Server Error
        """
        exception_info = traceback.format_exc()
        # Should add logging ...
        # app.logger.error(exception_info)
        return (
            render_template(
                "errors/500_error.html",
                exception_info=exception_info,
                version=lute.__version__,
                platform=platform.platform(),
                is_docker=current_app.env_config.is_docker,
            ),
            500,
        )

    @app.errorhandler(404)
    def _page_not_found(e):  # pylint: disable=unused-argument
        "Show custom error page on 404."
        return (
            render_template(
                "errors/404_error.html",
                version=lute.__version__,
                requested_url=request.url,
                referring_page=request.referrer,
            ),
            404,
        )


def _create_app(app_config, extra_config):
    """
    Create the app using the given configuration,
    and init the SqlAlchemy db.
    """

    app = Flask(__name__, instance_path=app_config.datapath)

    config = {
        "SECRET_KEY": "some_secret",
        "DATABASE": app_config.dbfilename,
        "ENV": app_config.env,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{app_config.dbfilename}",
        "DATAPATH": app_config.datapath,
        # ref https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
        # Don't track mods.
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    final_config = {**config, **extra_config}
    app.config.from_mapping(final_config)

    # Attach the app_config to app so it's available at runtime.
    app.env_config = app_config

    db.init_app(app)

    @listens_for(Pool, "connect")
    def _pragmas_on_connect(dbapi_con, con_record):  # pylint: disable=unused-argument
        dbapi_con.execute("pragma recursive_triggers = on;")

    with app.app_context():
        db.create_all()
        UserSetting.load()
        # TODO valid parsers: do parser check, mark valid as active, invalid as inactive.
        clean_data()
    app.db = db

    _add_base_routes(app, app_config)
    app.register_blueprint(language_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(term_bp)
    app.register_blueprint(termtag_bp)
    app.register_blueprint(read_bp)
    app.register_blueprint(bing_bp)
    app.register_blueprint(userimage_bp)
    app.register_blueprint(useraudio_bp)
    app.register_blueprint(termimport_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(themes_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(cli_bp)
    if app_config.is_test_db:
        app.register_blueprint(dev_api_bp)

    return app


def create_app(
    app_config_path=None,
    extra_config=None,
    output_func=None,
):
    """
    App factory.  Calls dbsetup, and returns Flask app.

    Args:
    - app_config_path: path to yml file.  If None, use root config or default.
    - extra_config: dict, e.g. pass { 'TESTING': True } during unit tests.
    """

    def null_print(s):  # pylint: disable=unused-argument
        pass

    outfunc = output_func or null_print

    if app_config_path is None:
        if os.path.exists("config.yml"):
            app_config_path = "config.yml"
        else:
            app_config_path = AppConfig.default_config_filename()

    app_config = AppConfig(app_config_path)
    _setup_app_dirs(app_config)
    setup_db(app_config, output_func)

    if extra_config is None:
        extra_config = {}
    outfunc("Initializing app.")
    app = _create_app(app_config, extra_config)

    outfunc("Initializing parsers from plugins ...")
    init_parser_plugins()
    outfunc("Enabled parsers:")
    for _, v in supported_parsers():
        outfunc(f"  * {v}")

    return app
