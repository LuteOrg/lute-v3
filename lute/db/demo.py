"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

from sqlalchemy import text
from lute.language.service import Service
from lute.book.model import Repository
from lute.book.stats import Service as StatsService
from lute.models.repositories import SystemSettingRepository
import lute.db.management

from lute.utils.debug_helpers import DebugTimer


def _demo_languages():
    """
    Demo languages to be loaded for new users.
    Also loaded during tests.
    """
    return [
        "Arabic",
        "Classical Chinese",
        "Czech",
        "English",
        "French",
        "German",
        "Greek",
        "Hindi",
        "Japanese",
        "Russian",
        "Sanskrit",
        "Spanish",
        "Turkish",
    ]


def set_load_demo_flag(session, flag_value):
    "Set the flag."
    repo = SystemSettingRepository(session)
    repo.set_value("LoadDemoData", flag_value)
    session.commit()


def should_load_demo_data(session):
    """
    True if LoadDemoData setting is true.
    """
    repo = SystemSettingRepository(session)
    s = repo.get_value("LoadDemoData")
    if s is None:
        return False
    return bool(int(s))


def contains_demo_data(session):
    """
    True if IsDemoData setting is present.
    """
    repo = SystemSettingRepository(session)
    ss = repo.get_value("IsDemoData")
    if ss is None:
        return False
    return True


def remove_flag(session):
    """
    Remove IsDemoData setting.
    """
    if not contains_demo_data(session):
        raise RuntimeError("Can't delete non-demo data.")

    repo = SystemSettingRepository(session)
    repo.delete_key("IsDemoData")
    session.commit()


def tutorial_book_id(session):
    """
    Return the book id of the tutorial.
    """
    if not contains_demo_data(session):
        return None
    sql = """select BkID from books
    inner join languages on LgID = BkLgID
    where LgName = 'English' and BkTitle = 'Tutorial'
    """
    r = session.execute(text(sql)).first()
    if r is None:
        return None
    return int(r[0])


def delete_demo_data(session):
    """
    If this is a demo, wipe everything.
    """
    if not contains_demo_data(session):
        raise RuntimeError("Can't delete non-demo data.")
    remove_flag(session)
    lute.db.management.delete_all_data(session)


# Loading demo data.


def load_demo_languages(session):
    """
    Load selected predefined languages.  Assume everything is supported.

    This method will also be called during acceptance tests, so it's public.
    """
    dt = DebugTimer("load_demo_languages")
    demo_langs = _demo_languages()
    dt.step("demo_langs")
    service = Service(session)
    langs = [service.get_language_def(langname)["language"] for langname in demo_langs]
    dt.step("langs")
    supported = [lang for lang in langs if lang.is_supported]
    dt.step("supported")
    for lang in supported:
        session.add(lang)
    dt.step("added to session")
    session.commit()
    dt.step("commit")


def load_demo_stories(session):
    "Load the stories."
    demo_langs = _demo_languages()
    service = Service(session)
    langdefs = [service.get_language_def(langname) for langname in demo_langs]
    langdefs = [d for d in langdefs if d["language"].is_supported]

    r = Repository(session)
    for d in langdefs:
        for b in d["books"]:
            print(b.title, flush=True)
            r.add(b)
    r.commit()

    repo = SystemSettingRepository(session)
    repo.set_value("IsDemoData", True)
    session.commit()

    svc = StatsService(session)
    svc.refresh_stats()


def _db_has_data(session):
    "True of the db contains any language data."
    sql = "select LgID from languages limit 1"
    r = session.execute(text(sql)).first()
    return r is not None


def load_demo_data(session):
    """
    Load the data.
    """
    if _db_has_data(session):
        set_load_demo_flag(session, False)
        return

    repo = SystemSettingRepository(session)
    do_load = repo.get_value("LoadDemoData")
    if do_load is None:
        # Only load if flag is explicitly set.
        return

    do_load = bool(int(do_load))
    if not do_load:
        return

    dt = DebugTimer("load_demo_data")
    load_demo_languages(session)
    dt.step("load_demo_languages")
    load_demo_stories(session)
    dt.step("load_demo_stories")
    repo.set_value("IsDemoData", True)
    repo.set_value("LoadDemoData", False)
    session.commit()
    DebugTimer.total_summary()
