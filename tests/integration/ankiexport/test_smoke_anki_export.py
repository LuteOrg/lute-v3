"""
Smoke test get post data.
"""

import json
from lute.models.term import Term, TermTag
from lute.db import db
from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.service import Service


def test_smoke_get_post_data(empty_db, spanish):
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

    spec = SrsExportSpec()
    spec.id = 1
    spec.export_name = "export_name"
    spec.criteria = ""
    spec.deck_name = "good_deck"
    spec.note_type = "good_note"
    spec.field_mapping = json.dumps({"a": "{ language }"})
    spec.active = True
    spec.field_mapping = json.dumps(
        {
            "a": "{ language }",
            "b": "{ image }",
            "c": "{ term }",
            "d": "{ sentence }",
        }
    )

    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b", "c", "d"]}
    svc = Service(anki_decks, anki_notes, [spec])
    post_data = svc.get_ankiconnect_post_data([term.id], {}, "dummyurl", db.session)
    # print(post_data, flush=True)

    expected = {
        1: {
            "export_name": {
                "action": "multi",
                "params": {
                    "actions": [
                        {
                            "action": "storeMediaFile",
                            "params": {
                                "filename": "LUTE_TERM_1.jpg",
                                "url": "dummyurl/userimages/1/blah.jpg",
                            },
                        },
                        {
                            "action": "addNote",
                            "params": {
                                "note": {
                                    "deckName": "good_deck",
                                    "modelName": "good_note",
                                    "fields": {
                                        "a": "Spanish",
                                        "b": '<img src="LUTE_TERM_1.jpg">',
                                        "c": "un gatito",
                                    },
                                    "tags": ["lute", "p_tag", "t_tag"],
                                }
                            },
                        },
                    ]
                },
            }
        }
    }

    assert post_data == expected, "Got post data"
