"""
Simple CLI commands.
"""

import click
from flask import Blueprint

from lute.cli.language_term_export import generate_file

bp = Blueprint("cli", __name__)


@bp.cli.command("hello")
def hello():
    "Say hello -- proof-of-concept CLI command only."
    msg = """
    Hello there!

    This is the Lute cli.

    There may be some experimental scripts here ...
    nothing that will change or damage your Lute data,
    but the CLI may change.

    Thanks for looking.
    """
    print(msg)


@bp.cli.command("language_export")
@click.argument("language")
@click.argument("output_path")
def language_export(language, output_path):
    """
    Get all terms from active books in the language, and write a
    data file of term frequencies and children.
    """
    generate_file(language, output_path)
