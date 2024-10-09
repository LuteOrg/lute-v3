"""
Bulk import books.
"""

import csv
import os
import sys

from lute.book.model import Book, Repository
from lute.db import db
from lute.models.language import Language


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
    repo = Repository(db)
    count = 0
    with open(file, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            book = Book()
            book.title = row['title']
            book.language_name = language
            if 'language' in row and row['language']:
                book.language_name = row['language']
            if not book.language_name:
                print("Skipping book with unspecified language: {}".format(book.title))
                continue
            lang = Language.find_by_name(book.language_name)
            if not lang:
                print("Skipping book with unknown language ({}): {}".format(book.language_name, book.title))
                continue
            if repo.find_by_title(book.title, lang.id) is not None:
                print("Already exists in {}: {}".format(book.language_name, book.title))
                continue
            count += 1
            all_tags = []
            if tags:
                all_tags.extend(tags)
            if 'tags' in row and row['tags']:
                for tag in row['tags'].split(','):
                    if tag and tag not in all_tags:
                        all_tags.append(tag)
            book.text = row['text']
            if 'url' in row and row['url']:
                book.source_uri = row['url']
            book.book_tags = all_tags
            if 'audio' in row and row['audio']:
                book.audio_filename = os.path.join(os.path.dirname(file), row['audio'])
            if 'bookmarks' in row and row['bookmarks']:
                book.audio_bookmarks = row['bookmarks']
            repo.add(book)
            print("Added {} book (tags={}): {}".format(book.language_name, ','.join(all_tags), book.title))

    print()
    print("Added {} books".format(count))
    print()

    if not commit:
        db.session.rollback()
        print("Dry run, no changes made.")
        return

    print("Committing...")
    sys.stdout.flush()
    repo.commit()
