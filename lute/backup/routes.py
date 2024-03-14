"""
Backup routes.

Backup settings form management, and running backups.
"""

import os
import traceback
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    jsonify,
    redirect,
    send_file,
    flash,
)
from lute.models.setting import BackupSettings
from lute.backup.service import create_backup, skip_this_backup, list_backups


bp = Blueprint("backup", __name__, url_prefix="/backup")


@bp.route("/index")
def index():
    """
    List all backups.
    """
    settings = BackupSettings.get_backup_settings()
    backups = list_backups(settings.backup_dir)
    backups.sort(reverse=True)

    return render_template(
        "backup/index.html", backup_dir=settings.backup_dir, backups=backups
    )


@bp.route("/download/<filename>")
def download_backup(filename):
    "Download the given backup file."
    settings = BackupSettings.get_backup_settings()
    fullpath = os.path.join(settings.backup_dir, filename)
    return send_file(fullpath, as_attachment=True)


@bp.route("/backup", methods=["GET"])
def backup():
    """
    Endpoint called from front page.

    With extra arg 'type' for manual.
    """
    backuptype = "automatic"
    if "type" in request.args:
        backuptype = "manual"

    settings = BackupSettings.get_backup_settings()
    return render_template(
        "backup/backup.html", backup_folder=settings.backup_dir, backuptype=backuptype
    )


@bp.route("/do_backup", methods=["POST"])
def do_backup():
    """
    Ajax endpoint called from backup.html.
    """
    backuptype = "automatic"
    prms = request.form.to_dict()
    if "type" in prms:
        backuptype = prms["type"]

    c = current_app.env_config
    settings = BackupSettings.get_backup_settings()
    is_manual = backuptype.lower() == "manual"
    try:
        f = create_backup(c, settings, is_manual=is_manual)
        flash(f"Backup created: {f}", "notice")
        return jsonify(f)
    except Exception as e:  # pylint: disable=broad-exception-caught
        tb = traceback.format_exc()
        return jsonify({"errmsg": str(e) + " -- " + tb}), 500


@bp.route("/skip_this_backup", methods=["GET"])
def handle_skip_this_backup():
    "Update last backup date so backup not attempted again."
    skip_this_backup()
    return redirect("/", 302)
