"""
Service, validates and posts.
"""

from lute.models.repositories import TermRepository
from lute.term.model import ReferencesRepository
from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.mapper import (
    mapping_as_array,
    get_values_and_media_mapping,
    validate_mapping,
    get_fields_and_final_values,
)
from lute.ankiexport.selector import (
    evaluate_selector,
    validate_selector,
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

        try:
            validate_selector(spec.criteria)
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

    def _all_terms(self, term):
        "Term and any parents."
        ret = [term]
        ret.extend(term.parents)
        return ret

    def _all_tags(self, term):
        "Tags for term and all parents."
        ret = [tt.text for t in self._all_terms(term) for tt in t.term_tags]
        return sorted(list(set(ret)))

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _build_ankiconnect_post_json(
        self,
        mapping_array,
        media_mappings,
        lute_and_term_tags,
        deck_name,
        model_name,
    ):
        "Build post json for term using the mappings."

        post_actions = []
        for new_filename, original_url in media_mappings.items():
            hsh = {
                "action": "storeMediaFile",
                "params": {
                    "filename": new_filename,
                    "url": original_url,
                },
            }
            post_actions.append(hsh)

        post_actions.append(
            {
                "action": "addNote",
                "params": {
                    "note": {
                        "deckName": deck_name,
                        "modelName": model_name,
                        "fields": {m.fieldname: m.value.strip() for m in mapping_array},
                        "tags": lute_and_term_tags,
                    }
                },
            }
        )

        return {"action": "multi", "params": {"actions": post_actions}}

    def get_ankiconnect_post_data_for_term(self, term, refsrepo):
        """
        Get post data for a single term.
        Separate method for unit testing.
        """
        self.validate_specs()

        use_exports = [
            spec
            for spec in self.export_specs
            if spec.active and evaluate_selector(spec.criteria, term)
        ]
        # print(f"Using {len(use_exports)} exports")

        ret = []
        for export in use_exports:
            replacements, mmap = get_values_and_media_mapping(
                term, refsrepo, export.field_mapping
            )
            mapping_array = get_fields_and_final_values(
                export.field_mapping, replacements
            )
            tags = ["lute"] + self._all_tags(term)

            p = self._build_ankiconnect_post_json(
                mapping_array,
                mmap,
                tags,
                export.deck_name,
                export.note_type,
            )
            ret.append(p)

        return ret

    def get_ankiconnect_post_data(self, term_ids, db_session):
        """
        Build data to be posted.

        Throws if any validation failure or mapping failure, as it's
        annoying to handle partial failures.
        """

        repo = TermRepository(db_session)
        refsrepo = ReferencesRepository(db_session)

        ret = {}
        for tid in term_ids:
            term = repo.find(tid)
            pd = self.get_ankiconnect_post_data_for_term(term, refsrepo)
            ret[tid] = pd

        return ret
