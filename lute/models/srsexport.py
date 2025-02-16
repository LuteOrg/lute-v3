"""
Srs export entity.
"""

from lute.db import db


class SrsExportSpec(db.Model):
    """
    Srs export spec entity.
    """

    __tablename__ = "srsexportspecs"

    id = db.Column("SrsID", db.Integer, primary_key=True)
    export_name = db.Column(
        "SrsExportName", db.String(200), nullable=False, unique=True
    )
    criteria = db.Column("SrsCriteria", db.String(1000), nullable=False)
    deck_name = db.Column("SrsDeckName", db.String(200), nullable=False)
    note_type = db.Column("SrsNoteType", db.String(200), nullable=False)
    field_mapping = db.Column("SrsFieldMapping", db.String(1000), nullable=False)
    active = db.Column("SrsActive", db.Boolean, nullable=False, default=True)
