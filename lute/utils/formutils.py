"""
Common form methods.
"""

from lute.models.language import Language
from lute.models.repositories import UserSettingRepository


def language_choices(session, dummy_entry_placeholder="-", include_inactive=False):
    """
    Return the list of languages for select boxes.

    If only one lang exists, only return that,
    otherwise add a '-' dummy entry at the top.
    """
    query = session.query(Language).order_by(Language.name)
    if not include_inactive:
        query = query.filter(Language.is_active == True)  # noqa: E712
    langs = query.all()
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
    try:
        current_language_id = repo.get_value("current_language_id")
    except Exception:  # pylint: disable=broad-exception-caught
        # Setting doesn't exist (e.g. restored from older version)
        current_language_id = None

    if current_language_id is None:
        valid_language_ids = [int(p[0]) for p in language_choices(session)]
        current_language_id = valid_language_ids[0] if valid_language_ids else 0
        try:
            repo.set_value("current_language_id", current_language_id)
            session.commit()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return current_language_id

    current_language_id = int(current_language_id)

    valid_language_ids = [int(p[0]) for p in language_choices(session)]
    if current_language_id in valid_language_ids:
        return current_language_id

    current_language_id = valid_language_ids[0]
    try:
        repo.set_value("current_language_id", current_language_id)
        session.commit()
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return current_language_id
