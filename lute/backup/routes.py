"""
Backup routes.

Backup settings form management, and running backups.
"""

import traceback
from flask import Blueprint, render_template, request, jsonify
from lute.models.setting import BackupSettings
from lute.backup.service import create_backup
from lute.config.app_config import AppConfig


bp = Blueprint("backup", __name__, url_prefix="/backup")


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

    c = AppConfig.create_from_config()
    settings = BackupSettings.get_backup_settings()
    is_manual = backuptype.lower() == "manual"
    try:
        f = create_backup(c, settings, is_manual=is_manual)
        return jsonify(f)
    except Exception as e:  # pylint: disable=broad-exception-caught
        tb = traceback.format_exc()
        return jsonify({"errmsg": str(e) + " -- " + tb}), 500
