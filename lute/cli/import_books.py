"""
Bulk import books.
"""

import csv
import os
import sys

from lute.book.model import Book, Repository
from lute.db import db


def import_books_from_csv(language, file, tags, commit):
    """
    Bulk import books from a CSV file.

    Args:

      language: the name of the language as it appears in your languages
                settings
      file:     the path to the CSV file to import (see lute/cli/commands.py
                for the requirements for this file).
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
            title = row['title']
            if repo.find_by_title(title) is not None:
                print("Already exists: {}".format(title))
                continue
            count += 1
            all_tags = []
            if tags:
                all_tags.extend(tags)
            if 'tags' in row and row['tags']:
                for tag in row['tags'].split(','):
                    if tag and tag not in all_tags:
                        all_tags.append(tag)
            book = Book()
            book.language_name = language
            book.title = row['title']
            book.text = row['text']
            if 'url' in row and row['url']:
                book.source_uri = row['url']
            book.book_tags = all_tags
            if 'audio' in row and row['audio']:
                book.audio_filename = os.path.join(os.path.dirname(file), row['audio'])
            if 'bookmarks' in row and row['bookmarks']:
                book.audio_bookmarks = row['bookmarks']
            repo.add(book)
            print("Added book (tags={}): {}".format(','.join(all_tags), book.title))

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
