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
from lute.db import db
from lute.models.repositories import UserSettingRepository
from lute.backup.service import Service, BackupException


bp = Blueprint("backup", __name__, url_prefix="/backup")


def _get_settings():
    "Get backup settings."
    repo = UserSettingRepository(db.session)
    return repo.get_backup_settings()


@bp.route("/index")
def index():
    """
    List all backups.
    """
    settings = _get_settings()
    service = Service(db.session)
    backups = service.list_backups(settings.backup_dir)
    backups.sort(reverse=True)

    return render_template(
        "backup/index.html", backup_dir=settings.backup_dir, backups=backups
    )


@bp.route("/download/<filename>")
def download_backup(filename):
    "Download the given backup file."
    settings = _get_settings()
    fullpath = os.path.join(settings.backup_dir, filename)
    return send_file(fullpath, as_attachment=True)


@bp.route("/upload", methods=["POST"])
def upload_backup():
    """
    Upload a backup file into the backup directory.
    """
    settings = _get_settings()
    service = Service(db.session)
    try:
        filename = service.save_uploaded_backup(
            settings, request.files.get("backup_file")
        )
        flash(f"Backup uploaded: {filename}", "notice")
    except BackupException as e:
        flash(str(e), "error")
    return redirect("/backup/index", 302)


@bp.route("/backup", methods=["GET"])
def backup():
    """
    Endpoint called from front page.

    With extra arg 'type' for manual.
    """
    backuptype = "automatic"
    if "type" in request.args:
        backuptype = "manual"

    settings = _get_settings()
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
    settings = _get_settings()
    service = Service(db.session)
    is_manual = backuptype.lower() == "manual"
    try:
        f = service.create_backup(c, settings, is_manual=is_manual)
        flash(f"Backup created: {f}", "notice")
        return jsonify(f)
    except Exception as e:  # pylint: disable=broad-exception-caught
        tb = traceback.format_exc()
        return jsonify({"errmsg": str(e) + " -- " + tb}), 500


@bp.route("/do_restore", methods=["POST"])
def do_restore():
    """
    Ajax endpoint to restore a backup file.
    """
    prms = request.form.to_dict()
    filename = prms.get("filename", "")

    c = current_app.env_config
    settings = _get_settings()
    service = Service(db.session)
    try:
        service.restore_backup(c, settings, filename)
        flash(f"Backup restored: {filename}", "notice")
        return jsonify(filename)
    except Exception as e:  # pylint: disable=broad-exception-caught
        tb = traceback.format_exc()
        return jsonify({"errmsg": str(e) + " -- " + tb}), 500


@bp.route("/do_delete", methods=["POST"])
def do_delete():
    """
    Ajax endpoint to delete a backup file.
    """
    prms = request.form.to_dict()
    filename = prms.get("filename", "")

    settings = _get_settings()
    service = Service(db.session)
    try:
        deleted_filename = service.delete_backup(settings, filename)
        flash(f"Backup deleted: {deleted_filename}", "notice")
        return jsonify(deleted_filename)
    except Exception as e:  # pylint: disable=broad-exception-caught
        tb = traceback.format_exc()
        return jsonify({"errmsg": str(e) + " -- " + tb}), 500


@bp.route("/skip_this_backup", methods=["GET"])
def handle_skip_this_backup():
    "Update last backup date so backup not attempted again."
    service = Service(db.session)
    service.skip_this_backup()
    return redirect("/", 302)
