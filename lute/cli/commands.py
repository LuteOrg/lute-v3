"""
Simple CLI commands.
"""

import click
from flask import Blueprint

from lute.cli.language_term_export import generate_language_file, generate_book_file

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
    Get all terms from all books in the language, and write a
    data file of term frequencies and children.
    """
    generate_language_file(language, output_path)


@bp.cli.command("book_term_export")
@click.argument("bookid")
@click.argument("output_path")
def book_term_export(bookid, output_path):
    """
    Get all terms for the given book, and write a
    data file of term frequencies and children.
    """
    generate_book_file(bookid, output_path)
