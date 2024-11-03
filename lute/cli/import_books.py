"""
Bulk import books.
"""

import csv
import os
import sys

from lute.book.model import Book, Repository
from lute.db import db
from lute.models.repositories import LanguageRepository


def import_books_from_csv(file, language, tags, commit):
    """
    Bulk import books from a CSV file.

    Args:

      file:     the path to the CSV file to import (see lute/cli/commands.py
                for the requirements for this file).
      language: the name of the language to use by default, as it appears in
                your languages settings
      tags:     a list of tags to apply to all books
      commit:   a boolean value indicating whether to commit the changes to the
                database. If false, a list of books to be imported will be
                printed out, but no changes will be made.
    """
    repo = Repository(db.session)
    lang_repo = LanguageRepository(db.session)

    count = 0
    with open(file, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            book = Book()
            book.title = row["title"]
            book.language_name = row.get("language") or language
            if not book.language_name:
                print(f"Skipping book with unspecified language: {book.title}")
                continue
            lang = lang_repo.find_by_name(book.language_name)
            if not lang:
                print(
                    f"Skipping book with unknown language ({book.language_name}): {book.title}"
                )
                continue
            if repo.find_by_title(book.title, lang.id) is not None:
                print(f"Already exists in {book.language_name}: {book.title}")
                continue
            count += 1
            all_tags = []
            if tags:
                all_tags.extend(tags)
            if "tags" in row and row["tags"]:
                for tag in row["tags"].split(","):
                    if tag and tag not in all_tags:
                        all_tags.append(tag)
            book.book_tags = all_tags
            book.text = row["text"]
            book.source_uri = row.get("url") or None
            if "audio" in row and row["audio"]:
                book.audio_filename = os.path.join(os.path.dirname(file), row["audio"])
            book.audio_bookmarks = row.get("bookmarks") or None
            repo.add(book)
            print(
                f"Added {book.language_name} book (tags={','.join(all_tags)}): {book.title}"
            )

    print()
    print(f"Added {count} books")
    print()

    if not commit:
        db.session.rollback()
        print("Dry run, no changes made.")
        return

    print("Committing...")
    sys.stdout.flush()
    repo.commit()
