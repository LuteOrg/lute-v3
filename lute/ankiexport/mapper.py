"""Field to value mapper.

e.g. given string like

lute_term_id: {{ id }}
term: {{ term }}
tags: {{ tags:["masc", "fem"] }}

extracts data from the given term and generates a mapping of field to
actual values to send to AnkiConnect.
"""

from dataclasses import dataclass
from lute.ankiexport.exceptions import AnkiExportConfigurationError


@dataclass
class FieldMappingData:
    "Data class"
    fieldname: str = None
    value: str = None


def mapping_as_array(field_mapping):
    """
    Given "a: {{ somefield }}", returns
    [ ("a", "{{ somefield }}") ]

    Raises config error if dup fields.
    """
    ret = []
    lines = [
        s.strip()
        for s in field_mapping.split("\n")
        if s.strip() != "" and not s.strip().startswith("#")
    ]
    for lin in lines:
        parts = lin.split(":", 1)
        if len(parts) != 2:
            raise AnkiExportConfigurationError(f'Bad mapping line "{lin}" in mapping')
        field, val = parts
        if field in [fmd.fieldname for fmd in ret]:
            raise AnkiExportConfigurationError(f"Dup field {field} in mapping")
        fmd = FieldMappingData()
        fmd.fieldname = field.strip()
        fmd.value = val.strip()
        ret.append(fmd)
    return ret
