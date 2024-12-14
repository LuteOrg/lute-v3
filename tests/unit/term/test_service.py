"""
Term service tests.
"""

import pytest
from lute.models.term import Term as DBTerm
from lute.models.repositories import TermRepository
from lute.db import db
from lute.term.service import Service
from tests.utils import add_terms

# Bulk parent update


def test_bulk_parent_update_smoke_test(app_context, spanish):
    "Update parent of term."
    [t, p] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [t.id])
    newt = TermRepository(db.session).find(t.id)
    assert [tp.text for tp in newt.parents] == ["p"], "P added as parent"


# test_parent_must_exist
# test_no_terms_ok
# test_all_terms_must_be_same_language
# with pytest.raises(FileNotFoundError, match="No such file"):
