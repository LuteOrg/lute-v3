"""
Development-only routes.

These routes are accessed during acceptance tests.
The acceptance tests don't have easy access to
the db model ... at least, as far as I can tell ...
so this is a quick-and-easy way to set some test
data state.

If there's a better way to manage this, I'll change
this.

These are dangerous methods that hack on the db data without
safeguards, so they can only be run against a test_ db.
"""

import os
from sqlalchemy import text
from flask import Blueprint, current_app, Response, jsonify, redirect, flash
from lute.models.language import Language
from lute.models.setting import UserSetting
import lute.parse.registry
from lute.db import db
import lute.db.management
import lute.db.demo


bp = Blueprint("dev_api", __name__, url_prefix="/dev_api")


@bp.before_request
def _ensure_is_test_db():
    "These methods should only be run on a test db!"
    if not current_app.env_config.is_test_db:
        raise RuntimeError("Dangerous method, only possible on test_lute database.")


@bp.route("/wipe_db", methods=["GET"])
def wipe_db():
    "Clean it all."
    lute.db.management.delete_all_data()
    flash("db wiped")
    return redirect("/", 302)


@bp.route("/load_demo", methods=["GET"])
def load_demo():
    "Clean out everything, and load the demo."
    lute.db.management.delete_all_data()
    lute.db.demo.load_demo_data()
    flash("demo loaded")
    return redirect("/", 302)


@bp.route("/load_demo_languages", methods=["GET"])
def load_demo_languages():
    "Clean out everything, and load the demo langs with dummy dictionaries."
    lute.db.management.delete_all_data()
    lute.db.demo.load_demo_languages()
    langs = db.session.query(Language).all()
    for lang in langs:
        lang.dictionaries[0].dicturi = f"/dev_api/dummy_dict/{lang.name}/###"
        db.session.add(lang)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/load_demo_stories", methods=["GET"])
def load_demo_stories():
    "Stories only.  No db wipe."
    lute.db.demo.load_demo_stories()
    flash("stories loaded")
    return redirect("/", 302)


@bp.route("/language_ids", methods=["GET"])
def get_lang_ids():
    "Get ids of all langs."
    langs = db.session.query(Language).all()
    ret = {}
    for lang in langs:
        ret[lang.name] = lang.id
    return jsonify(ret)


@bp.route("/delete_all_terms", methods=["GET"])
def delete_all_terms():
    "Delete all the terms only."
    db.session.query(text("DELETE FROM words"))
    db.session.commit()
    flash("terms deleted")
    return redirect("/", 302)


@bp.route("/sqlresult/<string:sql>", methods=["GET"])
def sql_result(sql):
    "Get the sql result as json."

    def clean_val(v):
        if v is None:
            return "NULL"
        if isinstance(v, str) and "\u200b" in v:
            return v.replace("\u200b", "/")
        return v

    content = []
    result = db.session.execute(text(sql)).all()
    for row in result:
        rowvals = [clean_val(v) for v in row]
        content.append("; ".join(map(str, rowvals)))

    return jsonify(content)


@bp.route("/dummy_dict/<string:langname>/<string:term>", methods=["GET"])
def dummy_language_dict(langname, term):
    "Fake language dictionary/term lookup."
    return Response(f"dev_api/dummy_dict/{langname}/{term}")


@bp.route("/disable_parser/<string:parsername>/<string:renameto>", methods=["GET"])
def disable_parser(parsername, renameto):
    "Hack: rename a parser in the registry so that languages can't find it."
    p = lute.parse.registry.__LUTE_PARSERS__
    if parsername in p:
        p[renameto] = p.pop(parsername)
    langs = db.session.query(Language).all()
    unsupported = [
        {"parser_type": lang.parser_type, "language": lang.name}
        for lang in langs
        if not lang.is_supported
    ]
    allparsers = [
        {"parser_type": lang.parser_type, "language": lang.name} for lang in langs
    ]
    available_types = list(p.keys())
    return jsonify(
        {
            "_unsupported": unsupported,
            "available_types": available_types,
            "parsers": allparsers,
        }
    )


@bp.route("/disable_backup", methods=["GET"])
def disable_backup():
    "Disables backup -- tests don't need to back up."
    UserSetting.set_value("backup_enabled", False)
    db.session.commit()
    flash("backup disabled")
    return redirect("/", 302)


@bp.route("/throw_error/<message>", methods=["GET"])
def throw_error(message):
    "Throw an error to ensure handler works!"
    raise RuntimeError(message)


@bp.route("/fake_story.html", methods=["GET"])
def fake_story():
    "Return a fake story for import book test."
    return Response(
        """<html>
    <head>
    <title>Mi perro.</title>
    </head>
    <body>
    <p>Hola. Tengo un perro.</p>
    </body>
    </html>"""
    )


@bp.route("/temp_file_content/<filename>", methods=["GET"])
def temp_file_content(filename):
    "Get the content of the file."
    fpath = os.path.join(current_app.env_config.temppath, filename)
    s = ""
    with open(fpath, "r", encoding="utf-8") as f:
        s = f.read()
    return s
