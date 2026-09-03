"""Verify fix: exported CSV (with status 99/98/0) can be reimported."""

import os
import tempfile

import pytest

from lute.db import db
from lute.language.service import Service as LanguageService
from lute.termimport.service import Service, BadImportFileError


def _import(content, **kwargs):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as f:
        f.write(content)
    try:
        return Service(db.session).import_file(path, **kwargs)
    finally:
        os.remove(path)


def _status(text):
    sql = "select WoStatus from words where WoText = :t"
    res = db.session.execute(db.text(sql), {"t": text}).scalar()
    return res


@pytest.fixture(name="spanish")
def given_demo(app_context):
    LanguageService(db.session).load_language_def("Spanish")


def test_roundtrip_status_99_98_0(spanish):
    content = (
        "language,term,translation,status\n"
        "Spanish,gato,cat,99\n"
        "Spanish,perro,dog,98\n"
        "Spanish,pajaro,bird,0\n"
        "Spanish,casa,house,\n"
    )
    stats = _import(content, create_terms=True, update_terms=True)
    assert stats == {"created": 4, "updated": 0, "skipped": 0}
    assert _status("gato") == 99, "well known"
    assert _status("perro") == 98, "ignored"
    assert _status("pajaro") == 0, "unknown placeholder"
    assert _status("casa") == 1, "blank -> 1"


def test_invalid_status_still_rejected(spanish):
    with pytest.raises(BadImportFileError, match="Status must be one of"):
        _import("language,term,translation,status\nSpanish,gato,cat,7\n")
