"""
Term mapping tests.
"""

import pytest
from bs4 import BeautifulSoup
import html
from lute.models.term import Term, TermTag
from lute.db import db
from tests.dbasserts import assert_sql_result


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

    response = client.get(f"/read/termpopup/{term.id}")

    decoded_response = response.data.decode(
        "utf-8"
    )  # Decode byte string to regular string
    unescaped_response = html.unescape(decoded_response)  # Unescape HTML entities

    # Optionally format the HTML for readability
    soup = BeautifulSoup(unescaped_response, "html.parser")
    pretty_response = soup.prettify()

    print(pretty_response, flush=True)

    for t in ["t", "p", "c"]:
        for part in ["trans", "rom", "tag"]:
            s = f"{t}_{part}"
            assert s in pretty_response, s
