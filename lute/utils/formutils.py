"""
Common form methods.
"""

from lute.models.language import Language
from lute.models.repositories import UserSettingRepository


def language_choices(session, dummy_entry_placeholder="-"):
    """
    Return the list of languages for select boxes.

    If only one lang exists, only return that,
    otherwise add a '-' dummy entry at the top.
    """
    langs = session.query(Language).order_by(Language.name).all()
    supported = [lang for lang in langs if lang.is_supported]
    lang_choices = [(s.id, s.name) for s in supported]
    # Add a dummy placeholder even if there are no languages.
    if len(lang_choices) != 1:
        lang_choices = [(0, dummy_entry_placeholder)] + lang_choices
    return lang_choices


def valid_current_language_id(session):
    """
    Get the current language id from UserSetting, ensuring
    it's still valid.  If not, change it.
    """
    repo = UserSettingRepository(session)
    current_language_id = repo.get_value("current_language_id")
    current_language_id = int(current_language_id)

    valid_language_ids = [int(p[0]) for p in language_choices(session)]
    if current_language_id in valid_language_ids:
        return current_language_id

    current_language_id = valid_language_ids[0]
    repo.set_value("current_language_id", current_language_id)
    session.commit()
    return current_language_id
