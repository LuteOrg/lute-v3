"""
Service, validates and posts.
"""

from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.mapper import (
    mapping_as_array,
    # get_values_and_media_mapping,
    validate_mapping,
    # get_fields_and_final_values,
)


class Service:
    "Srs export service."

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

    def _validate_single_spec(self, spec):
        """
        Returns array of errors if any for the given spec.
        """
        errors = []
        if spec.deck_name not in self.anki_deck_names:
            errors.append(f'No deck name: "{spec.deck_name}"')

        if spec.note_type not in self.anki_note_types_and_fields:
            errors.append(f'No note type: "{spec.note_type}"')
        else:
            note_fields = self.anki_note_types_and_fields.get(spec.note_type, {})
            mapping_array = mapping_as_array(spec.field_mapping)
            fieldnames = [m.fieldname for m in mapping_array]
            bad_fields = [f for f in fieldnames if f not in note_fields]
            if len(bad_fields) > 0:
                bad_fields = ", ".join(bad_fields)
                msg = f"Note type {spec.note_type} does not have field(s): {bad_fields}"
                errors.append(msg)

        try:
            validate_mapping(spec.field_mapping)
        except AnkiExportConfigurationError as ex:
            errors.append(str(ex))

        return errors

    def validate_specs(self):
        """
        Return hash of spec ids and any config errors.
        """
        failures = {}
        for spec in self.export_specs:
            v = self._validate_single_spec(spec)
            if len(v) != 0:
                failures[spec.id] = "; ".join(v)
        return failures

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
