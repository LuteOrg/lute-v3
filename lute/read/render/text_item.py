"TextItem class."

zws = "\u200B"  # zero-width space


class TextItem:  # pylint: disable=too-many-instance-attributes
    """
    Unit to be rendered.

    Data structure for template read/textitem.html

    Some elements are lazy loaded, because they're only needed in
    certain situations.
    """

    def __init__(self, term=None):
        self.index: int
        self.lang_id: int
        self.text: str  # The original, un-overlapped text.
        self.text_lc: str
        self.is_word: int

        # Number of tokens originally in the Text item.
        self.token_count: int = 1

        # Number of tokens that should be displayed, starting from the
        # end of the string.
        self.display_count: int = 1

        self.sentence_number: int = 0
        self.paragraph_number: int = 0

        # Calls setter
        self.term = term

        self.extra_html_classes = []

        # TODO code
        # # The flash message can be None, so we need an extra flag
        # # to determine if it has been loaded or not.
        # self._flash_message_loaded: bool = False
        # self._flash_message: str = None

    def __repr__(self):
        return f'<TextItem "{self.text}" (wo_id={self.wo_id}, sent={self.sentence_number})>'

    @property
    def term(self):
        return self._term

    @property
    def wo_id(self):
        "The term id is the wo_id."
        if self._term is None:
            return None
        return self._term.id

    @term.setter
    def term(self, t):
        self.wo_status = None
        self._term = t
        if t is None:
            return
        self.lang_id = t.language.id
        self.wo_status = t.status

    # TODO - reactivate with non-lazy query results.
    # @property
    # def flash_message(self):
    #     """
    #     Return flash message if anything present.
    #     Lazy loaded as needed.
    #     """
    #     if self._flash_message_loaded:
    #         return self._flash_message
    #     if self.term is None:
    #         return None

    #     self._flash_message = self.term.get_flash_message()
    #     self._flash_message_loaded = True
    #     return self._flash_message

    @property
    def display_text(self):
        "Show last n tokens, if some of the textitem is covered."
        toks = self.text.split(zws)
        disp_toks = toks[-self.display_count :]
        return zws.join(disp_toks)

    @property
    def html_display_text(self):
        """
        Content to be rendered to browser.
        """
        return self.display_text.replace(zws, "")

    @property
    def span_id(self):
        """
        Each span gets a unique id.
        """
        return f"ID-{self.sentence_number}-{self.index}"

    @property
    def status_class(self):
        "Status class to apply."
        if self.wo_id is None:
            return "status0"
        return f"status{self.wo_status}"

    def add_html_class(self, c):
        "Add extra class to term."
        self.extra_html_classes.append(c)

    @property
    def html_class_string(self):
        """
        Create class string for TextItem.
        """
        if self.is_word == 0:
            return "textitem"

        classes = [
            "textitem",
            "click",
            "word",
            "word" + str(self.wo_id),
        ]

        if self.display_text != self.text:
            classes.append("overlapped")
        classes.extend(self.extra_html_classes)

        return " ".join(classes)
