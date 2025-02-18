"""
Service, validates and posts.
"""

import json
from lute.models.repositories import TermRepository
from lute.term.model import ReferencesRepository
from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.field_mapping import (
    get_values_and_media_mapping,
    validate_mapping,
    get_fields_and_final_values,
    SentenceLookup,
)
from lute.ankiexport.criteria import (
    evaluate_criteria,
    validate_criteria,
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
        self.anki_deck_names = anki_deck_names
        self.anki_note_types_and_fields = anki_note_types_and_fields
        self.export_specs = export_specs

    def validate_spec(self, spec):
        """
        Returns array of errors if any for the given spec.
        """
        if not spec.active:
            return []

        errors = []

        try:
            validate_criteria(spec.criteria)
        except AnkiExportConfigurationError as ex:
            errors.append(str(ex))

        if spec.deck_name not in self.anki_deck_names:
            errors.append(f'No deck name "{spec.deck_name}"')

        valid_note_type = spec.note_type in self.anki_note_types_and_fields
        if not valid_note_type:
            errors.append(f'No note type "{spec.note_type}"')

        mapping = None
        try:
            mapping = json.loads(spec.field_mapping)
        except json.decoder.JSONDecodeError:
            errors.append("Mapping is not valid json")

        if valid_note_type and mapping:
            note_fields = self.anki_note_types_and_fields.get(spec.note_type, {})
            bad_fields = [f for f in mapping.keys() if f not in note_fields]
            if len(bad_fields) > 0:
                bad_fields = ", ".join(bad_fields)
                msg = f"Note type {spec.note_type} does not have field(s): {bad_fields}"
                errors.append(msg)

        if mapping:
            try:
                validate_mapping(json.loads(spec.field_mapping))
            except AnkiExportConfigurationError as ex:
                errors.append(str(ex))

        return errors

    def validate_specs(self):
        """
        Return hash of spec ids and any config errors.
        """
        failures = {}
        for spec in self.export_specs:
            v = self.validate_spec(spec)
            if len(v) != 0:
                failures[spec.id] = "; ".join(v)
        return failures

    def validate_specs_failure_message(self):
        "Failure message for alerts."
        failures = self.validate_specs()
        msgs = []
        for k, v in failures.items():
            spec = next(s for s in self.export_specs if s.id == k)
            msgs.append(f"{spec.export_name}: {v}")
        return msgs

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
        mapping,
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
                        "fields": mapping,
                        "tags": lute_and_term_tags,
                    }
                },
            }
        )

        return {"action": "multi", "params": {"actions": post_actions}}

    def get_ankiconnect_post_data_for_term(self, term, base_url, sentence_lookup):
        """
        Get post data for a single term.
        This assumes that all the specs are valid!
        Separate method for unit testing.
        """
        use_exports = [
            spec
            for spec in self.export_specs
            if spec.active and evaluate_criteria(spec.criteria, term)
        ]
        # print(f"Using {len(use_exports)} exports")

        ret = {}
        for export in use_exports:
            mapping = json.loads(export.field_mapping)
            replacements, mmap = get_values_and_media_mapping(
                term, sentence_lookup, mapping
            )
            for k, v in mmap.items():
                mmap[k] = base_url + v
            updated_mapping = get_fields_and_final_values(mapping, replacements)
            tags = ["lute"] + self._all_tags(term)

            p = self._build_ankiconnect_post_json(
                updated_mapping,
                mmap,
                tags,
                export.deck_name,
                export.note_type,
            )
            ret[export.export_name] = p

        return ret

    def get_ankiconnect_post_data(
        self, term_ids, termid_sentences, base_url, db_session
    ):
        """
        Build data to be posted.

        Throws if any validation failure or mapping failure, as it's
        annoying to handle partial failures.
        """

        msgs = self.validate_specs_failure_message()
        if len(msgs) > 0:
            show_msgs = [f"* {m}" for m in msgs]
            show_msgs = "\n".join(show_msgs)
            err_msg = "Anki export configuration errors:\n" + show_msgs
            raise AnkiExportConfigurationError(err_msg)

        repo = TermRepository(db_session)

        refsrepo = ReferencesRepository(db_session)
        sentence_lookup = SentenceLookup(termid_sentences, refsrepo)

        ret = {}
        for tid in term_ids:
            term = repo.find(tid)
            pd = self.get_ankiconnect_post_data_for_term(
                term, base_url, sentence_lookup
            )
            if len(pd) > 0:
                ret[tid] = pd

        return ret
