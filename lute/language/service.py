"Language helper methods."

import os
import re
from glob import glob
import yaml
from lute.models.language import Language
from lute.book.model import Book, Repository


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def get_supported_defs(self):
        "Return supported language definitions."
        ret = []
        def_glob = os.path.join(self._language_defs_path(), "**", "definition.yaml")
        for f in glob(def_glob):
            lang = None
            with open(f, "r", encoding="utf-8") as df:
                d = yaml.safe_load(df)
                lang = Language.from_dict(d)
            if lang.is_supported:
                entry = {"language": lang, "books": self._get_books(f, lang.name)}
                ret.append(entry)
        ret.sort(key=lambda x: x["language"].name)
        return ret

    def predefined_languages(self):
        "Languages defined in yaml files."
        return [d["language"] for d in self.get_supported_defs()]

    def _get_books(self, lang_definition_filename, lang_name):
        "Get the stories in the same directory as the definition.yaml."
        books = []
        d, f = os.path.split(lang_definition_filename)
        story_glob = os.path.join(d, "*.txt")
        for filename in glob(story_glob):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            title_match = re.search(r"title:\s*(.*)\n", content)
            title = title_match.group(1).strip()
            content = re.sub(r"#.*\n", "", content)
            b = Book()
            b.language_name = lang_name
            b.title = title
            b.text = content
            books.append(b)
        return books

    def get_language_def(self, lang_name):
        "Get a lang def and its stories."
        defs = self.get_supported_defs()
        ret = [d for d in defs if d["language"].name == lang_name]
        if len(ret) == 0:
            raise RuntimeError(f"Missing language def name {lang_name}")
        return ret[0]

    def load_language_def(self, lang_name):
        "Load a language def and its stories, save to database."
        load_def = self.get_language_def(lang_name)
        lang = load_def["language"]
        self.session.add(lang)
        self.session.commit()

        r = Repository(self.session)
        for b in load_def["books"]:
            r.add(b)
        r.commit()

        return lang.id

    def _language_defs_path(self):
        "Path to the definitions and stories."
        thisdir = os.path.dirname(__file__)
        d = os.path.join(thisdir, "..", "db", "language_defs")
        return os.path.abspath(d)
