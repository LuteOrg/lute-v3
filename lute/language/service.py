"Language helper methods."

import os
import re
from glob import glob
import yaml
from lute.models.language import Language
from lute.book.model import Book, Repository

# from lute.utils.debug_helpers import DebugTimer


class LangDef:
    "Language, built from language definition.yml, and .txt book files."

    # Map of definition.yaml directory to the yaml.safe_load content.
    # The definition files never change, and loading them takes time, so
    # cache it for better unit test performance.
    yaml_cache = {}

    @classmethod
    def _get_loaded_yaml(cls, definition_file_path):
        "Get from cache, or load it and return it."
        if definition_file_path not in LangDef.yaml_cache:
            with open(definition_file_path, "r", encoding="utf-8") as df:
                d = yaml.safe_load(df)
                LangDef.yaml_cache[definition_file_path] = d
        return LangDef.yaml_cache[definition_file_path]

    def __init__(self, directory):
        "Build from files."
        self.directory = directory
        self.language_name = self._get_name(directory)

    def _get_name(self, directory):
        def_file = os.path.join(directory, "definition.yaml")
        d = LangDef._get_loaded_yaml(def_file)
        return d["name"]

    @property
    def language(self):
        return self._load_lang_def(self.directory)

    @property
    def books(self):
        return self._get_books(self.directory, self.language_name)

    def _load_lang_def(self, directory):
        "Load from file, must exist."
        def_file = os.path.join(directory, "definition.yaml")
        d = LangDef._get_loaded_yaml(def_file)
        return Language.from_dict(d)

    def _get_books(self, directory, language_name):
        "Get the stories."
        books = []
        story_glob = os.path.join(directory, "*.txt")
        for filename in glob(story_glob):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            title_match = re.search(r"title:\s*(.*)\n", content)
            title = title_match.group(1).strip()
            content = re.sub(r"#.*\n", "", content)
            b = Book()
            b.language_name = language_name
            b.title = title
            b.text = content
            books.append(b)
        return books


class Service:
    "Service."

    def __init__(self, session):
        self.session = session
        self.lang_defs_cache = self._get_langdefs_cache()

    def _get_langdefs_cache(self):
        "Load cache."
        # dt = DebugTimer("_get_langdefs_cache", False)
        # dt.step("start")
        thisdir = os.path.dirname(__file__)
        langdefs_dir = os.path.join(thisdir, "..", "db", "language_defs")
        langdefs_dir = os.path.abspath(langdefs_dir)
        # dt.step("got base directory")
        cache = []
        def_glob = os.path.join(langdefs_dir, "**", "definition.yaml")
        def_list = glob(def_glob)
        # dt.step("globbed")
        def_list.sort()
        for f in def_list:
            lang_dir, _ = os.path.split(f)
            ld = LangDef(lang_dir)
            # dt.step(f"build ld {ld.language_name}".ljust(30))
            cache.append(ld)
        # dt.summary()
        return cache

    def get_supported_defs(self):
        "Return supported language definitions."
        ret = [ld for ld in self.lang_defs_cache if ld.language.is_supported]
        ret.sort(key=lambda x: x.language_name)
        return ret

    def supported_predefined_languages(self):
        "Supported Languages defined in yaml files."
        return [d.language for d in self.get_supported_defs()]

    def get_language_def(self, lang_name):
        "Get a lang def and its stories."
        ret = [ld for ld in self.lang_defs_cache if ld.language_name == lang_name]
        if len(ret) == 0:
            raise RuntimeError(f"Missing language def name {lang_name}")
        return ret[0]

    def load_language_def(self, lang_name):
        "Load a language def and its stories, save to database."
        load_def = self.get_language_def(lang_name)
        lang = load_def.language
        if not lang.is_supported:
            raise RuntimeError(f"{lang_name} not supported, can't be loaded.")

        self.session.add(lang)
        self.session.commit()

        r = Repository(self.session)
        for b in load_def.books:
            r.add(b)
        r.commit()

        return lang.id
