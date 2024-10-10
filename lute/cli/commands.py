"""
Simple CLI commands.
"""

import click
from flask import Blueprint

from lute.cli.language_term_export import generate_language_file, generate_book_file
from lute.cli.import_books import import_books_from_csv

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


@bp.cli.command("import_books_from_csv")
@click.option(
    "--commit",
    is_flag=True,
    help="""
    Commit the changes to the database. If not set, import in dry-run mode. A
    list of changes will be printed out but not applied.
""",
)
@click.option(
    "--tags",
    default="",
    help="""
    A comma-separated list of tags to apply to all books.
""",
)
@click.option(
    "--language",
    default="",
    help="""
    The name of the default language to apply to each book, as it appears in
    your language settings. If unset, the language must be indicated in the
    "language" column of the CSV file.
""",
)
@click.argument("file")
def import_books_from_csv_cmd(language, file, tags, commit):
    """
    Import books from a CSV file.

    The CSV file must have a header row with the following, case-sensitive,
    column names. The order of the columns does not matter. The CSV file may
    include additional columns, which will be ignored.

      - title: the title of the book

      - text: the text of the book

      - language: [optional] the name of the language of book, as it appears in
      your language settings. If unspecified, the language specified on the
      command line (using the --language option) will be used.

      - url: [optional] the source URL for the book

      - tags: [optional] a comma-separated list of tags to apply to the book
      (e.g., "audiobook,beginner")

      - audio: [optional] the path to the audio file of the book. This should
      either be an absolute path, or a path relative to the CSV file.

      - bookmarks: [optional] a semicolon-separated list of audio bookmark
      positions, in seconds (decimals permitted; e.g., "12.34;42.89;89.00").
    """
    tags = list(tags.split(",")) if tags else []
    import_books_from_csv(file, language, tags, commit)
