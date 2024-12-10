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
from lute.models.repositories import SystemSettingRepository, LanguageRepository
import lute.db.management


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


def set_load_demo_flag(session):
    "Set the flag."
    repo = SystemSettingRepository(session)
    repo.set_value("LoadDemoData", True)
    session.commit()


def remove_load_demo_flag(session):
    "Set the flag."
    repo = SystemSettingRepository(session)
    repo.delete_key("LoadDemoData")
    session.commit()


def _flag_exists(session, flagname):
    "True if flag exists, else false."
    repo = SystemSettingRepository(session)
    return repo.key_exists(flagname)


def should_load_demo_data(session):
    return _flag_exists(session, "LoadDemoData")


def contains_demo_data(session):
    return _flag_exists(session, "IsDemoData")


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
    Load selected predefined languages, if they're supported.

    This method will also be called during acceptance tests, so it's public.
    """
    demo_langs = _demo_languages()
    service = Service(session)
    langs = [service.get_language_def(langname).language for langname in demo_langs]
    supported = [lang for lang in langs if lang.is_supported]
    for lang in supported:
        session.add(lang)
    session.commit()


def load_demo_stories(session):
    "Load the stories for any languages already loaded."
    demo_langs = _demo_languages()
    service = Service(session)
    langdefs = [service.get_language_def(langname) for langname in demo_langs]

    langrepo = LanguageRepository(session)
    langdefs = [
        d
        for d in langdefs
        if d.language.is_supported
        and langrepo.find_by_name(d.language.name) is not None
    ]

    r = Repository(session)
    for d in langdefs:
        for b in d.books:
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
        remove_load_demo_flag(session)
        return

    repo = SystemSettingRepository(session)
    do_load = repo.get_value("LoadDemoData")
    if do_load is None:
        # Only load if flag is explicitly set.
        return

    do_load = bool(int(do_load))
    if not do_load:
        return

    load_demo_languages(session)
    load_demo_stories(session)
    remove_load_demo_flag(session)
    repo.set_value("IsDemoData", True)
    session.commit()
