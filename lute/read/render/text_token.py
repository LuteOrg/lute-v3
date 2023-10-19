"""
TextToken class.
"""

class TextToken:
    """
    TODO documentation: what is this needed for?
    """
    txid = 0
    sentence_number = 0
    paragraph_number = 0  # Derived during RenderableSentence loading.
    order = 0
    is_word = 0
    tok_text = None


    @staticmethod
    def create_from(parsed_tokens):
        """
        Create array of TextTokens from the array of ParsedTokens.
        """
        ret = []

        sentence_number = 0
        para_number = 0
        tok_order = 0

        for pt in parsed_tokens:
            tok = TextToken()
            tok.tok_text = pt.token
            tok.is_word = pt.is_word

            tok.order = tok_order
            tok.sentence_number = sentence_number
            tok.paragraph_number = para_number

            # Increment counters after the TextToken has been
            # completed, so that it belongs to the correct
            # sentence/paragraph.
            tok_order += 1
            if pt.is_end_of_sentence:
                sentence_number += 1
            if pt.token == '¶':
                para_number += 1

            ret.append(tok)

        return ret
