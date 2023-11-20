"""
Simple CLI commands.
"""

import click
from flask import Blueprint

bp = Blueprint("cli", __name__)


@bp.cli.command("hello")
def hello():
    "Say hi."
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
    "TODO - export data."
    print(f"TODO: export {language} data to {output_path}.")
