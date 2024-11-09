"""
Reading rendering helpers.
"""

import itertools
import re
from sqlalchemy import text as sqltext

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.calculate_textitems import get_textitems as calc_get_textitems
from lute.read.render.multiword_indexer import MultiwordTermIndexer

# from lute.utils.debug_helpers import DebugTimer


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def find_all_Terms_in_string(self, s, language):  # pylint: disable=too-many-locals
        """
        Find all terms contained in the string s.

        For example
        - given s = "Here is a cat"
        - given terms in the db: [ "cat", "a cat", "dog" ]

        This would return the terms "cat" and "a cat".
        """
        cleaned = re.sub(r" +", " ", s)
        tokens = language.get_parsed_tokens(cleaned)
        return self._find_all_terms_in_tokens(tokens, language)

    def _get_multiword_terms(self, language):
        "Get all multiword terms."
        sql = sqltext(
            """
            SELECT WoID, WoTextLC FROM words
            WHERE WoLgID=:language_id and WoTokenCount>1
            """
        )
        sql = sql.bindparams(language_id=language.id)
        return self.session.execute(sql).all()

    def _find_all_multi_word_term_text_lcs_in_content(self, text_lcs, language):
        "Find multiword terms, return list of text_lcs."

        # There are a few ways of finding multi-word Terms
        # (with token_count > 1) in the content:
        #
        # 1. load each mword term text_lc via sql and check.
        # 2. using the model
        # 3. SQL with "LIKE"
        #
        # During reasonable test runs with my data, the times in seconds
        # for each are similar (~0.02, ~0.05, ~0.025).  This method is
        # only used for small amounts of data, and the user experience hit
        # is negligible, so I'll use the first method which IMO is the clearest
        # code.

        zws = "\u200B"  # zero-width space
        content = zws + zws.join(text_lcs) + zws

        # Method 1:
        reclist = self._get_multiword_terms(language)
        return [p[1] for p in reclist if f"{zws}{p[1]}{zws}" in content]

        ## # Method 2: use the model.
        ## contained_term_qry = self.session.query(Term).filter(
        ##     Term.language == language,
        ##     Term.token_count > 1,
        ##     func.instr(content, Term.text_lc) > 0,
        ## )
        ## return [r.text_lc for r in contained_term_qry.all()]

        ## # Method 3: Query with LIKE
        ## sql = sqltext(
        ##     """
        ##     SELECT WoTextLC FROM words
        ##     WHERE WoLgID=:lid and WoTokenCount>1
        ##     AND :content LIKE '%' || :zws || WoTextLC || :zws || '%'
        ##     """
        ## )
        ## sql = sql.bindparams(lid=language.id, content=content, zws=zws)
        ## recs = self.session.execute(sql).all()
        ## return [r[0] for r in recs]

    def _find_all_terms_in_tokens(self, tokens, language, kwtree=None):
        """
        Find all terms contained in the (ordered) parsed tokens tokens.

        For example
        - given tokens = "Here", " ", "is", " ", "a", " ", "cat"
        - given terms in the db: [ "cat", "a/ /cat", "dog" ]

        This would return the terms "cat" and "a/ /cat".

        Method:
        - build list of lowercase text in the tokens
        - append all multword term strings that exist in the content
        - query for Terms that exist in the list

        Note: this method only uses indexes for multiword terms, as any
        content analyzed is first parsed into tokens before being passed
        to this routine.  There's no need to search for single-word Terms
        in the tokenized strings, they can be found by a simple query.
        """

        # Performance: About half of the time in this routine is spent in
        # Step 1 (finding multiword terms), the rest in step 2 (the actual
        # query).
        # dt = DebugTimer("_find_all_terms_in_tokens", display=True)

        parser = language.parser
        text_lcs = [parser.get_lowercase(t.token) for t in tokens]

        # Step 1: get the multiwords in the content.
        if kwtree is None:
            mword_terms = self._find_all_multi_word_term_text_lcs_in_content(
                text_lcs, language
            )
        else:
            results = kwtree.search_all(text_lcs)
            mword_terms = [r[0] for r in results]
        # dt.step("filtered mword terms")

        # Step 2: load the Term objects.
        #
        # The Term fetch is actually performant -- there is no
        # real difference between loading the Term objects versus
        # loading raw data with SQL and getting dicts.
        #
        # Code for getting raw data:
        # param_keys = [f"w{i}" for i, _ in enumerate(text_lcs)]
        # keys_placeholders = ','.join([f":{k}" for k in param_keys])
        # param_dict = dict(zip(param_keys, text_lcs))
        # param_dict["langid"] = language.id
        # sql = sqltext(f"""SELECT WoID, WoTextLC FROM words
        #     WHERE WoLgID=:langid and WoTextLC in ({keys_placeholders})""")
        # sql = sql.bindparams(language.id, *text_lcs)
        # results = self.session.execute(sql, param_dict).fetchall()
        text_lcs.extend(mword_terms)
        tok_strings = list(set(text_lcs))
        terms_matching_tokens_qry = self.session.query(Term).filter(
            Term.text_lc.in_(tok_strings), Term.language == language
        )
        all_terms = terms_matching_tokens_qry.all()
        # dt.step("exec query")

        return all_terms

    def get_textitems(self, s, language, multiword_term_indexer=None):
        """
        Get array of TextItems for the string s.

        The multiword_term_indexer is a big performance boost, but takes
        time to initialize.
        """
        # Hacky reset of state of ParsedToken state.
        # _Shouldn't_ be needed but doesn't hurt, even if it's lame.
        ParsedToken.reset_counters()

        cleaned = re.sub(r" +", " ", s)
        tokens = language.get_parsed_tokens(cleaned)
        terms = self._find_all_terms_in_tokens(tokens, language, multiword_term_indexer)
        textitems = calc_get_textitems(tokens, terms, language, multiword_term_indexer)
        return textitems

    def get_multiword_indexer(self, language):
        "Return indexer loaded with all multiword terms."
        mw = MultiwordTermIndexer()
        for r in self._get_multiword_terms(language):
            mw.add(r[1])
        return mw

    def get_paragraphs(self, s, language):
        """
        Get array of arrays of TextItems for the given string s.

        This doesn't use an indexer, as it should only be used
        for a single page of text!
        """
        textitems = self.get_textitems(s, language)

        def _split_textitems_by_paragraph(textitems):
            "Split by ¶"
            ret = []
            curr_para = []
            for t in textitems:
                if t.text == "¶":
                    ret.append(curr_para)
                    curr_para = []
                else:
                    curr_para.append(t)
            if len(curr_para) > 0:
                ret.append(curr_para)
            return ret

        def _split_by_sentence_number(p):
            sentences = [
                list(sentence)
                for _, sentence in itertools.groupby(p, key=lambda t: t.sentence_number)
            ]
            for s in sentences:
                s[0].add_html_class("sentencestart")
            return sentences

        paras = [
            _split_by_sentence_number(list(sentences))
            for sentences in _split_textitems_by_paragraph(textitems)
        ]

        return paras
