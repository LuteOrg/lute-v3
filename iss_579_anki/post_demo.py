"""
Demo posting a term.

Given term ID, get the term object:

- use selectors to determine what mappings should be used
- then generate the post bodies for anki connect
- do post

> select woid from words where wotextlc = 'kinder';
143771

"""

from lute.term.model import Term, Repository
import lute.app_factory
from lute.db import db

app = lute.app_factory.create_app()
with app.app_context():
    repo = Repository(db.session)
    t = repo.load(143771)
    print(t)
