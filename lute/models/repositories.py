"""
Repositories.
"""

from sqlalchemy import text as sqltext, and_, func
from lute.db import db
from lute.models.setting import UserSetting, BackupSettings, SystemSetting
from lute.models.language import Language
from lute.models.term import Term, TermTag
from lute.models.book import Book, BookTag


class SettingRepositoryBase:
    "Repository."

    def __init__(self, session, classtype):
        self.session = session
        self.classtype = classtype

    def key_exists_precheck(self, keyname):
        """
        Check key validity for certain actions.
        """

    def set_value(self, keyname, keyvalue):
        "Set, but don't save, a setting."
        self.key_exists_precheck(keyname)
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is None:
            s = self.classtype()
            s.key = keyname
        s.value = keyvalue
        self.session.add(s)

    def key_exists(self, keyname):
        "True if exists."
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        no_key = s is None
        return not no_key

    def get_value(self, keyname):
        "Get the saved key, or None if it doesn't exist."
        self.key_exists_precheck(keyname)
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is None:
            return None
        return s.value

    def delete_key(self, keyname):
        "Delete a key."
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is not None:
            self.session.delete(s)


class MissingUserSettingKeyException(Exception):
    """
    Cannot set or get unknown user keys.
    """


class UserSettingRepository(SettingRepositoryBase):
    "Repository."

    def __init__(self, session):
        super().__init__(session, UserSetting)

    def key_exists_precheck(self, keyname):
        """
        User keys must exist.
        """
        if not self.key_exists(keyname):
            raise MissingUserSettingKeyException(keyname)

    def get_backup_settings(self):
        "Convenience method."
        bs = BackupSettings()

        def _bool(v):
            return v in (1, "1", "y", True)

        bs.backup_enabled = _bool(self.get_value("backup_enabled"))
        bs.backup_auto = _bool(self.get_value("backup_auto"))
        bs.backup_warn = _bool(self.get_value("backup_warn"))
        bs.backup_dir = self.get_value("backup_dir")
        bs.backup_count = int(self.get_value("backup_count") or 5)
        bs.last_backup_datetime = self.get_last_backup_datetime()
        return bs

    def get_last_backup_datetime(self):
        "Get the last_backup_datetime as int, or None."
        v = self.get_value("lastbackup")
        if v is None:
            return None
        return int(v)

    def set_last_backup_datetime(self, v):
        "Set and save the last backup time."
        self.set_value("lastbackup", v)
        self.session.commit()


class SystemSettingRepository(SettingRepositoryBase):
    "Repository."

    def __init__(self, session):
        super().__init__(session, SystemSetting)


class LanguageRepository:
    "Repository."

    def __init__(self, session):
        self.session = session

    def find(self, language_id):
        "Get by ID."
        return self.session.query(Language).filter(Language.id == language_id).first()

    def find_by_name(self, name):
        "Get by name."
        return (
            self.session.query(Language)
            .filter(func.lower(Language.name) == func.lower(name))
            .first()
        )

    def all_dictionaries(self):
        "All dictionaries for all languages."
        lang_dicts = {}
        for lang in db.session.query(Language).all():
            lang_dicts[lang.id] = {
                "term": lang.active_dict_uris("terms"),
                "sentence": lang.active_dict_uris("sentences"),
            }
        return lang_dicts


class TermTagRepository:
    "Repository."

    def __init__(self, session):
        self.session = session

    def find(self, termtag_id):
        "Get by ID."
        return self.session.query(TermTag).filter(TermTag.id == termtag_id).first()

    def find_by_text(self, text):
        "Find a tag by text, or None if not found."
        return self.session.query(TermTag).filter(TermTag.text == text).first()

    def find_or_create_by_text(self, text):
        "Return tag or create one."
        ret = self.find_by_text(text)
        if ret is not None:
            return ret
        return TermTag(text)


class TermRepository:
    "Repository."

    def __init__(self, session):
        self.session = session

    def find(self, term_id):
        "Get by ID."
        return self.session.query(Term).filter(Term.id == term_id).first()

    def find_by_spec(self, spec):
        """
        Find by the given spec term's language ID and text.
        Returns None if not found.
        """
        langid = spec.language.id
        text_lc = spec.text_lc
        query = self.session.query(Term).filter(
            and_(Term.language_id == langid, Term.text_lc == text_lc)
        )
        terms = query.all()
        if not terms:
            return None
        return terms[0]

    def delete_empty_images(self):
        """
        Data clean-up: delete empty images.

        The code was leaving empty images in the db, which are obviously no good.
        This is a hack to clean up the data.
        """
        sql = "delete from wordimages where trim(WiSource) = ''"
        self.session.execute(sqltext(sql))
        self.session.commit()


class BookTagRepository:
    "Repository."

    def __init__(self, session):
        self.session = session

    def find_or_create_by_text(self, text):
        "Return tag or create one."
        ret = db.session.query(BookTag).filter(BookTag.text == text).first()
        if ret is not None:
            return ret
        return BookTag.make_book_tag(text)


class BookRepository:
    "Repository."

    def __init__(self, session):
        self.session = session

    def find(self, book_id):
        "Get by ID."
        return self.session.query(Book).filter(Book.id == book_id).first()

    def find_by_title(self, book_title, language_id):
        "Get by title."
        return (
            self.session.query(Book)
            .filter(and_(Book.title == book_title, Book.language_id == language_id))
            .first()
        )
