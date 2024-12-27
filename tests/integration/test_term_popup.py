"""
Term mapping tests.
"""

import html
from bs4 import BeautifulSoup
from lute.models.term import Term, TermTag
from lute.models.repositories import UserSettingRepository
from lute.db import db


def test_smoke_popup_response(client, empty_db, spanish):
    "Misc data check - parent and tags are saved."
    term = Term(spanish, "un gatito")
    term.translation = "t_trans\nt_extra"
    term.romanization = "t_rom"
    term.set_flash_message("hello")
    term.add_term_tag(TermTag("t_tag"))
    term.set_current_image("blah.jpg")

    parent = Term(spanish, "un gato")
    parent.translation = "p_trans\np_extra"
    parent.romanization = "p_rom"
    parent.add_term_tag(TermTag("p_tag"))
    parent.set_current_image("parentblah.jpg")

    component = Term(spanish, "gatito")
    component.translation = "c_trans\nc_extra"
    component.romanization = "c_rom"
    component.add_term_tag(TermTag("c_tag"))

    term.add_parent(parent)
    db.session.add(term)
    db.session.add(component)
    db.session.commit()

    term.set_flash_message("hello")

    db.session.add(term)
    db.session.add(parent)
    db.session.add(component)
    db.session.commit()

    def _get_pretty_response(term_id):
        "Response for term popup."
        response = client.get(f"/read/termpopup/{term_id}")
        decoded_response = response.data.decode("utf-8")
        unescaped_response = html.unescape(decoded_response)
        soup = BeautifulSoup(unescaped_response, "html.parser")
        pretty_response = soup.prettify()
        return pretty_response

    pretty_response = _get_pretty_response(term.id)
    print(pretty_response, flush=True)
    for t in ["t", "p", "c"]:
        for part in ["trans", "rom", "tag"]:
            s = f"{t}_{part}"
            assert s in pretty_response, s

    us_repo = UserSettingRepository(db.session)
    us_repo.set_value("term_popup_show_components", False)
    db.session.commit()
    pretty_response = _get_pretty_response(term.id)
    print(pretty_response, flush=True)
    for part in ["trans", "rom", "tag"]:
        s = f"c_{part}"
        assert s not in pretty_response, s
