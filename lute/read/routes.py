"""
/read endpoints.
"""

from flask import Blueprint, render_template, request

bp = Blueprint('read', __name__, url_prefix='/read')

@bp.route('/<int:bookid>/page/<int:pagenum>', methods=['GET'])
def read(bookid, pagenum):
    "Display reading pane for book page."
    # Simulate data retrieval for Book and TextRepository
    book = get_book_by_id(BkID)  # Implement a function to retrieve the book
    text = get_text_at_page_number(book, pagenum)  # Implement a function to retrieve the text
    text_title = text.getTitle()  # Implement the getTitle method

    pc = book.getPageCount()
    
    def page_in_range(n):
        if n < 1:
            n = 1
        if n > pc:
            n = pc
        return n

    pagenum = page_in_range(pagenum)
    prevpage = page_in_range(pagenum - 1)
    nextpage = page_in_range(pagenum + 1)
    prev10 = page_in_range(pagenum - 10)
    next10 = page_in_range(pagenum + 10)

    # TODO book: set the book.currentpage db
    # facade = ReadingFacade()
    # facade.set_current_book_text(text)
    # TODO book stats: mark stale for recalc later
    # BookStats.markStale(book)

    return render_template('read/index.html', text=text, htmltitle=text_title, book=book,
                           pagenum=pagenum, pagecount=pc, prevpage=prevpage, prev10page=prev10,
                           nextpage=nextpage, next10page=next10)

@app.route('/text/<int:TxID>', methods=['GET'])
def read_text(TxID):
    "Display a text."
    # Simulate data retrieval for Text and ReadingFacade
    text = get_text_by_id(TxID)  # Implement a function to retrieve the text

    # Simulate data retrieval for Book and Language
    book = text.getBook()
    lang = book.getLanguage()
    isRTL = lang.isLgRightToLeft() if lang else False

    facade = ReadingFacade()
    paragraphs = facade.getParagraphs(text)

    return render_template('read/text.html', textid=TxID, isRTL=isRTL,
                           dictionary_url=lang.getLgGoogleTranslateURI() if lang else None,
                           paragraphs=paragraphs)
