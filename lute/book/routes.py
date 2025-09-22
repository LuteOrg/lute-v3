"""
/book routes.
"""

import json
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    flash,
    current_app,
)
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.book.service import (
    Service as BookService,
    BookImportException,
    BookDataFromUrl,
)
from lute.tts.service import TTSService  # Add this import
from lute.book.datatables import get_data_tables_list
from lute.book.forms import NewBookForm, EditBookForm
from lute.book.stats import Service as StatsService
import lute.utils.formutils
from lute.db import db
from lute.models.language import Language
from lute.models.repositories import (
    BookRepository,
    UserSettingRepository,
    LanguageRepository,
)
from lute.book.model import Book, Repository


bp = Blueprint("book", __name__, url_prefix="/book")


def _load_term_custom_filters(request_form, parameters):
    "Manually add filters that the DataTablesFlaskParamParser doesn't know about."
    filter_param_names = [
        "filtLanguage",
    ]
    request_params = request_form.to_dict(flat=True)
    for p in filter_param_names:
        parameters[p] = request_params.get(p)


def datatables_source(is_archived):
    "Get datatables json for books."
    # In the future, we might want to create an API such as
    # get_books(sort_order, search_string, length, index, language_id).
    # See DataTablesFlaskParamParser.parse_params_2(request.form)
    # (currently unused)
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    _load_term_custom_filters(request.form, parameters)
    data = get_data_tables_list(parameters, is_archived, db.session)
    return jsonify(data)


@bp.route("/datatables/active", methods=["POST"])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route("/archived", methods=["GET"])
def archived():
    "List archived books."
    language_choices = lute.utils.formutils.language_choices(
        db.session, "(all languages)"
    )
    current_language_id = lute.utils.formutils.valid_current_language_id(db.session)

    return render_template(
        "book/index.html",
        status="Archived",
        language_choices=language_choices,
        current_language_id=current_language_id,
    )


# Archived must be capitalized, or the ajax call 404's.
@bp.route("/datatables/Archived", methods=["POST"])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


def _book_from_url(url):
    "Get data for a new book, or flash an error if can't parse."
    service = BookService()
    bd = None
    try:
        bd = service.book_data_from_url(url)
    except BookImportException as e:
        flash(e.message, "notice")
        bd = BookDataFromUrl()
    b = Book()
    b.title = bd.title
    b.source_uri = bd.source_uri
    b.text = bd.text
    return b


def _language_is_rtl_map():
    """
    Return language-id to is_rtl map, to be used during book creation.
    """
    ret = {}
    for lang in db.session.query(Language).all():
        ret[lang.id] = lang.right_to_left
    return ret


@bp.route("/new", methods=["GET", "POST"])
def new():
    "Create a new book, either from text or from a file."
    b = Book()
    import_url = request.args.get("importurl", "").strip()
    if import_url != "":
        b = _book_from_url(import_url)

    form = NewBookForm(obj=b)
    form.language_id.choices = lute.utils.formutils.language_choices(db.session)
    repo = Repository(db.session)

    if form.validate_on_submit():
        try:
            form.populate_obj(b)
            # Add the TTS option from the form
            b.generate_tts = form.generate_tts.data
            svc = BookService()
            book = svc.import_book(b, db.session)
            return redirect(f"/read/{book.id}/page/1", 302)
        except BookImportException as e:
            flash(e.message, "notice")
        except Exception as e:
            # Handle any other exceptions that might occur
            error_msg = f"An error occurred while creating the book: {str(e)}"
            flash(error_msg, "notice")
            # Log the full traceback for debugging
            import traceback
            print(f"Book creation error: {error_msg}")
            print(traceback.format_exc())

    # Don't set the current language before submit.
    usrepo = UserSettingRepository(db.session)
    current_language_id = int(usrepo.get_value("current_language_id"))
    form.language_id.data = current_language_id

    return render_template(
        "book/create_new.html",
        book=b,
        form=form,
        tags=repo.get_book_tags(),
        rtl_map=json.dumps(_language_is_rtl_map()),
        show_language_selector=True,
    )


@bp.route("/edit/<int:bookid>", methods=["GET", "POST"])
def edit(bookid):
    "Edit a book - can only change a few fields."
    repo = Repository(db.session)
    b = repo.load(bookid)
    form = EditBookForm(obj=b)

    if form.validate_on_submit():
        form.populate_obj(b)
        svc = BookService()
        svc.import_book(b, db.session)
        flash(f"{b.title} updated.")
        return redirect("/", 302)

    lang_repo = LanguageRepository(db.session)
    lang = lang_repo.find(b.language_id)
    return render_template(
        "book/edit.html",
        book=b,
        title_direction="rtl" if lang.right_to_left else "ltr",
        form=form,
        tags=repo.get_book_tags(),
    )


@bp.route("/import_webpage", methods=["GET", "POST"])
def import_webpage():
    return render_template("book/import_webpage.html")


def _find_book(bookid):
    "Find book from db."
    br = BookRepository(db.session)
    return br.find(bookid)


@bp.route("/archive/<int:bookid>", methods=["POST"])
def archive(bookid):
    "Archive a book."
    b = _find_book(bookid)
    b.archived = True
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/unarchive/<int:bookid>", methods=["POST"])
def unarchive(bookid):
    "Archive a book."
    b = _find_book(bookid)
    b.archived = False
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/delete/<int:bookid>", methods=["POST"])
def delete(bookid):
    "Archive a book."
    b = _find_book(bookid)
    db.session.delete(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/table_stats/<int:bookid>", methods=["GET"])
def table_stats(bookid):
    "Get the stats, return ajax."
    b = _find_book(bookid)
    if b is None or b.language is None:
        # Playwright tests were sometimes passing an id that didn't exist ...
        # I believe this is due to page caching, i.e. the book listing
        # is showing books and IDs that no longer exist after cache reset.
        # TODO fix_hack: get rid of this hack.
        return jsonify({})
    svc = StatsService(db.session)
    stats = svc.get_stats(b)
    ret = {
        "distinctterms": stats.distinctterms,
        "distinctunknowns": stats.distinctunknowns,
        "unknownpercent": stats.unknownpercent,
        "status_distribution": stats.status_distribution,
    }
    return jsonify(ret)


# Add a global variable to store progress (in a real application, you'd use a proper storage mechanism)
tts_progress = {}

# Add a route to get TTS progress
@bp.route("/tts_progress/<task_id>")
def tts_progress_status(task_id):
    """Get the progress of a TTS generation task."""
    progress_data = tts_progress.get(task_id, {"percent": 0, "message": "Not started"})
    return jsonify(progress_data)

# Add a route for async book creation with TTS
@bp.route("/new_async", methods=["POST"])
def new_async():
    """Create a new book asynchronously with TTS progress tracking."""
    import uuid
    import threading
    from flask import current_app
    
    task_id = str(uuid.uuid4())
    tts_progress[task_id] = {"percent": 0, "message": "Starting..."}
    
    # Store form data for processing in the background thread
    form_data = request.form.to_dict()
    files_data = {}
    if 'textfile' in request.files and request.files['textfile'].filename != '':
        file = request.files['textfile']
        files_data['textfile'] = {
            'filename': file.filename,
            'content': file.read()
        }
    if 'audiofile' in request.files and request.files['audiofile'].filename != '':
        file = request.files['audiofile']
        files_data['audiofile'] = {
            'filename': file.filename,
            'content': file.read()
        }
    
    # Define progress callback that updates our global progress tracker
    def progress_callback(percent, message):
        tts_progress[task_id] = {"percent": percent, "message": message}
        print(f"TTS Progress [{task_id}]: {percent}% - {message}")
    
    # Process in background thread
    def process_book(app, form_data, files_data, progress_callback):
        try:
            # Create the new book using the actual BookService
            # We need to use the application context in the thread
            with app.app_context():
                book_service = BookService()
                new_book = book_service.create_book(form_data, files_data, db.session, progress_callback)
                progress_callback(100, "Book creation complete!")
        except Exception as e:
            progress_callback(-1, f"Error: {str(e)}")
    
    thread = threading.Thread(
        target=process_book, 
        args=(current_app._get_current_object(), form_data, files_data, progress_callback)
    )
    thread.start()

    
    return jsonify({"task_id": task_id})
