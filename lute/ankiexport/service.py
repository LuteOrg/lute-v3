"""
Service, validates and posts.
"""

from lute.ankiexport.exceptions import AnkiExportConfigurationError


class Service:
    def __init__(
        self,
        anki_deck_names,
        anki_note_types_and_fields,
        export_specs,
    ):
        "init"
        self.fake_fail_counter = 0
        self.anki_deck_names = anki_deck_names
        self.anki_note_types_and_fields = anki_note_types_and_fields
        self.export_specs = export_specs

    def validate_specs(self):
        """
        Return hash of spec ids and any config errors.
        """
        return {}

    def _get_multiple_post_jsons(self, term_id):
        """Get data from service."""
        self.fake_fail_counter += 1
        if self.fake_fail_counter % 3 == 0:
            raise AnkiExportConfigurationError(
                f"dummy failure {self.fake_fail_counter}"
            )
        return [{"some": f"value_{term_id}"}]

    def get_ankiconnect_post_data(self, term_ids):
        """
        Build data to be posted.

        Throws if any validation failure or mapping failure, as it's
        annoying to handle partial failures.
        """

        ret = {tid: self._get_multiple_post_jsons(tid) for tid in term_ids}
        return ret
