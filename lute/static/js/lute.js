/* Lute functions. */

/**
 * The current term index (either clicked or hovered over)
 */
let LUTE_CURR_TERM_DATA_ORDER = -1;  // initially not set.


/**
 * When the reading pane is first loaded, it's in "hover mode",
 * meaning that when the user hovers over a word, that word becomes
 * the "active word" -- i.e., status update keyboard shortcuts should
 * operate on that hovered word, and as the user moves the mouse
 * around, the "active word" changes.  When a word is clicked, though,
 * there can't be any "hover changes", because the user should be
 * editing the word in the Term edit pane, and has to consciously
 * disable the "clicked word" mode by hitting ESC or RETURN.
 *
 * The full page text is often reloaded via ajax, e.g. when the user
 * saves an edited term, or the status is updated with a hotkey.
 * The template lute/templates/read/page_content.html calls
 * this method on reload to reset the cursor etc.
 */
function start_hover_mode(should_clear_frames = true) {
  $('span.kwordmarked').removeClass('kwordmarked');

  const curr_word = $('span.word').filter(function() {
    return _get_order($(this)) == LUTE_CURR_TERM_DATA_ORDER;
  });
  if (curr_word.length == 1) {
    const w = $(curr_word[0]);
    $(w).addClass('wordhover');
    apply_status_class($(w));
  }

  if (should_clear_frames) {
    $('#wordframeid').attr('src', '/read/empty');
    $('.dictcontainer').hide();
  }

  clear_newmultiterm_elements();

  // https://stackoverflow.com/questions/35022716/keydown-not-detected-until-window-is-clicked
  $(window).focus();
}


/** 
 * Prepare the interaction events with the text.
 *
 * pos = position hash, e.g.
 * {my: 'center bottom', at: 'center top-10', collision: 'flipfit flip'}
 */
function prepareTextInteractions(pos) {
  const t = $('#thetext');
  // Using "t.on" here because .word elements
  // are added and removed dynamically, and "t.on"
  // ensures that events remain for each element.
  t.on('mousedown', '.word', select_started);
  t.on('mouseover', '.word', select_over);
  t.on('mouseup', '.word', select_ended);

  t.on('mouseover', '.word', hover_over);
  t.on('mouseout', '.word', hover_out);

  if (!_show_highlights()) {
    t.on('mouseover', '.word', hover_over_add_status_class);
    t.on('mouseout', '.word', remove_status_highlights);
  }

  $(document).on('keydown', handle_keydown);

  $('#thetext').tooltip({
    position: pos,
    items: '.word.showtooltip',
    show: { easing: 'easeOutCirc' },
    content: function (setContent) { tooltip_textitem_hover_content($(this), setContent); }
  });
}


/**
 * Build the html content for jquery-ui tooltip.
 */
let tooltip_textitem_hover_content = function (el, setContent) {
  elid = parseInt(el.data('wid'));
  $.ajax({
    url: `/read/termpopup/${elid}`,
    type: 'get',
    success: function(response) {
      setContent(response);
    }
  });
}


function _show_wordframe_url(url) {
  top.frames.wordframe.location.href = url;
  applyInitialPaneSizes();  // in resize.js
}


function show_term_edit_form(el) {
  const wid = parseInt(el.data('wid'));
  _show_wordframe_url(`/read/edit_term/${wid}`);
}


function show_multiword_term_edit_form(selected) {
  if (selected.length == 0)
    return;
  const textparts = selected.toArray().map((el) => $(el).text());
  const text = textparts.join('').trim();
  if (text == "")
    return;
  const lid = parseInt(selected.eq(0).data('lang-id'));
  _show_wordframe_url(`/read/termform/${lid}/${text}`);
}


/* ========================================= */
/** Cursor management. */

/** Called on page load (read/index.html). */
function reset_cursor() {
  LUTE_CURR_TERM_DATA_ORDER = -1;
}

let _get_order = function(el) { return parseInt(el.data('order')); };

let save_curr_data_order = function(el) {
  LUTE_CURR_TERM_DATA_ORDER = _get_order(el);
}


/* ========================================= */
/** Status highlights.
 * There is a "show_highlights" UserSetting.
 *
 * If showing highlights, then the highlights are shown when the page
 * is rendered; otherwise, they're only shown/removed on hover enter/exit.
 *
 * User setting "show_highlights" is rendered in read/index.html. */

/** True if show_highlights setting is True. */
let _show_highlights = function() {
  return ($("#show_highlights").text().toLowerCase() == "true");
}

/**
 * Terms have data-status-class attribute.  If highlights should be shown,
 * then add that value to the actual span. */
function add_status_classes() {
  if (!_show_highlights())
    return;
  $('span.word').toArray().forEach(function (w) {
    apply_status_class($(w));
  });
}

/** Add the data-status-class to the term's classes. */
let apply_status_class = function(el) {
  el.addClass(el.data("status-class"));
}

/** Remove the status from elements, if not showing highlights. */
let remove_status_highlights = function() {
  if (_show_highlights()) {
    /* Not removing anything, always showing highlights. */
    return;
  }
  $('span.word').toArray().forEach(function (m) {
    el = $(m);
    el.removeClass(el.data("status-class"));
  });
}

/** Hover and term status classes */
function hover_over_add_status_class(e) {
  remove_status_highlights();
  apply_status_class($(this));
}


/* ========================================= */
/** Hovering */

function hover_over(e) {
  $('span.wordhover').removeClass('wordhover');
  const marked_count = $('span.kwordmarked').toArray().length;
  if (marked_count == 0) {
    $(this).addClass('wordhover');
    save_curr_data_order($(this));
  }
}

function hover_out(e) {
  $('span.wordhover').removeClass('wordhover');
}


/* ========================================= */
/** Clicking */

let word_clicked = function(el, e) {
  el.removeClass('wordhover');
  save_curr_data_order(el);

  // If already clicked, remove the click marker.
  if (el.hasClass('kwordmarked')) {
    el.removeClass('kwordmarked');
    if ($('span.kwordmarked').length == 0) {
      el.addClass('wordhover');
      start_hover_mode();
    }
    return;
  }

  // Not already clicked.
  if (! e.shiftKey) {
    // Only one element should be marked clicked.
    $('span.kwordmarked').removeClass('kwordmarked');
    show_term_edit_form(el);
  }
  el.addClass('kwordmarked');
  el.removeClass('hasflash');
}


/* ========================================= */
/** Multiword selection */

let selection_start_el = null;

let clear_newmultiterm_elements = function() {
  $('.newmultiterm').removeClass('newmultiterm');
  selection_start_el = null;
}

function select_started(e) {
  clear_newmultiterm_elements();
  $(this).addClass('newmultiterm');
  selection_start_el = $(this);
  save_curr_data_order($(this));
}

let get_selected_in_range = function(start_el, end_el) {
  let tmp_start = _get_order(start_el);
  let tmp_end = _get_order(end_el);
  // Javascript sorts numbers as strings.  wtf.
  const [startord, endord] = [tmp_start, tmp_end].sort((a, b) => a - b);
  const selected = $('span.textitem').filter(function() {
    const ord = _get_order($(this));
    return ord >= startord && ord <= endord;
  });
  return selected;
};

function select_over(e) {
  if (selection_start_el == null)
    return;  // Not selecting
  $('.newmultiterm').removeClass('newmultiterm');
  const selected = get_selected_in_range(selection_start_el, $(this));
  selected.addClass('newmultiterm');
}

function select_ended(e) {
  // Handle single word click.
  if (selection_start_el.attr('id') == $(this).attr('id')) {
    clear_newmultiterm_elements();
    word_clicked($(this), e);
    return;
  }

  $('span.kwordmarked').removeClass('kwordmarked');

  const selected = get_selected_in_range(selection_start_el, $(this));
  if (e.shiftKey) {
    copy_text_to_clipboard(selected.toArray());
    start_hover_mode(false);
    return;
  }

  show_multiword_term_edit_form(selected);
  selection_start_el = null;
}


/********************************************/
// Keyboard navigation.

/** Get the rest of the textitems in the current active/hovered word's
 * sentence or paragraph, or null if no selection. */
let get_textitems_spans = function(e) {
  let elements = $('span.kwordmarked, span.newmultiterm, span.wordhover');
  elements.sort((a, b) => _get_order($(a)) - _get_order($(b)));
  if (elements.length == 0)
    return elements;

  const w = elements[0];
  const attr_name = e.shiftKey ? 'paragraph-id' : 'sentence-id';
  const attr_value = $(w).data(attr_name);
  return $(`span.textitem[data-${attr_name}="${attr_value}"]`).toArray();
};

/** Copy the text of the textitemspans to the clipboard, and add a
 * color flash. */
let handle_copy = function(e) {
  tis = get_textitems_spans(e);
  copy_text_to_clipboard(tis);
}

let copy_text_to_clipboard = function(textitemspans) {
  const copytext = textitemspans.map(s => $(s).text()).join('');
  if (copytext == '')
    return;

  // console.log('copying ' + copytext);
  var textArea = document.createElement("textarea");
  textArea.value = copytext;
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand("Copy");
  textArea.remove();

  const removeFlash = function() {
    // console.log('removing flash');
    $('span.flashtextcopy').addClass('wascopied'); // for acceptance testing.
    $('span.flashtextcopy').removeClass('flashtextcopy');
  };

  // Add flash, set timer to remove.
  removeFlash();
  textitemspans.forEach(function (t) {
    $(t).addClass('flashtextcopy');
  });
  setTimeout(() => removeFlash(), 1000);

  $('#wordframeid').attr('src', '/read/flashcopied');
}


let move_cursor = function(shiftby) {
  // Cursor is set to the first clicked or hovered element.
  let elements = $('span.kwordmarked, span.newmultiterm, span.wordhover');
  elements.sort((a, b) => _get_order($(a)) - _get_order($(b)));
  const curr = (elements.length == 0) ? null : elements[0];

  let words = $('span.word');
  words.sort((a, b) => _get_order($(a)) - _get_order($(b)));

  let _get_new_index = function(curr) {
    if (curr == null)
      return 0;
    const pid = $(curr).attr('id');
    let i = words.toArray().findIndex(e => $(e).attr('id') == pid) + shiftby;
    i = Math.max(i, 0); // ensure >= 0
    i = Math.min(i, words.length - 1);  // within array.
    return i;
  }
  const target = $(words[_get_new_index(curr)]);

  // Adjust all screen state.
  $('span.newmultiterm').removeClass('newmultiterm');
  $('span.kwordmarked').removeClass('kwordmarked');
  $('span.wordhover').removeClass('wordhover');
  remove_status_highlights();
  target.addClass('kwordmarked');
  save_curr_data_order(target);
  apply_status_class(target);
  $(window).scrollTo(target, { axis: 'y', offset: -150 });
  show_term_edit_form(target, { autofocus: false });
}


/** SENTENCE TRANSLATIONS *************************/

// LUTE_SENTENCE_LOOKUP_URIS is rendered in templates/read/index.html.
// Hitting "t" repeatedly cycles through the uris.  Moving to a new
// sentence resets the order.

var LUTE_LAST_SENTENCE_TRANSLATION_TEXT = '';
var LUTE_CURR_SENTENCE_TRANSLATION_DICT_INDEX = 0;

/** Cycle through the LUTE_SENTENCE_LOOKUP_URIS.
 * If the current sentence is the same as the last translation,
 * move to the next sentence dictionary; otherwise start the cycle
 * again (from index 0).
 */
let _get_translation_dict_index = function(sentence) {
  const dict_count = LUTE_SENTENCE_LOOKUP_URIS.length;
  if (dict_count == 0)
    return 0;
  let new_index = LUTE_CURR_SENTENCE_TRANSLATION_DICT_INDEX;
  if (LUTE_LAST_SENTENCE_TRANSLATION_TEXT != sentence) {
    // New sentence, start at beginning.
    new_index = 0;
  }
  else {
    // Same sentence, next dict.
    new_index += 1;
    if (new_index >= dict_count)
      new_index = 0;
  }
  LUTE_LAST_SENTENCE_TRANSLATION_TEXT = sentence;
  LUTE_CURR_SENTENCE_TRANSLATION_DICT_INDEX = new_index;
  return new_index;
}


let show_translation_for_text = function(text) {
  if (text == '')
    return;

  if (LUTE_SENTENCE_LOOKUP_URIS.length == 0) {
    console.log('No sentence translation uris configured.');
    return;
  }

  const dict_index = _get_translation_dict_index(text);
  const userdict = LUTE_SENTENCE_LOOKUP_URIS[dict_index];

  const lookup = encodeURIComponent(text);
  const url = userdict.replace('###', lookup);
  if (url[0] == '*') {
    const finalurl = url.substring(1);  // drop first char.
    let settings = 'width=800, height=600, scrollbars=yes, menubar=no, resizable=yes, status=no';
    if (LUTE_USER_SETTINGS.open_popup_in_new_tab)
      settings = null;
    window.open(finalurl, 'dictwin', settings);
  }
  else {
    top.frames.wordframe.location.href = url;
    $('#read_pane_right').css('grid-template-rows', '1fr 0');
  }

};


/** Show the translation using the next dictionary. */
let show_sentence_translation = function(e) {
  const tis = get_textitems_spans(e);
  const sentence = tis.map(s => $(s).text()).join('');
  show_translation_for_text(sentence);
}


/** Translation for the full page. */
function show_page_translation() {
  let fulltext = $('#thetext p').map(function() {
    return $(this).find('span.textitem').map(function() {
      return $(this).text();
    }).get().join('');
  }).get().join('\n');
  fulltext = fulltext.replace(/\u200B/g, '');
  show_translation_for_text(fulltext);
}


/** THEMES AND HIGHLIGHTS *************************/
/* Change to the next theme, and reload the page. */
function next_theme() {
  $.ajax({
    url: '/theme/next',
    type: 'post',
    dataType: 'JSON',
    contentType: 'application/json',
    success: function(response) {
      location.reload();
    },
    error: function(response, status, err) {
      const msg = {
        response: response,
        status: status,
        error: err
      };
      console.log(`failed: ${JSON.stringify(msg, null, 2)}`);
    }
  });

}

function toggleFocus() {
  const focusChk = document.getElementById("focus");
  const event = new Event("change");
  focusChk.checked = !focusChk.checked;
  focusChk.dispatchEvent(event);
}

/* Toggle highlighting, and reload the page. */
function toggle_highlight() {
  $.ajax({
    url: '/theme/toggle_highlight',
    type: 'post',
    dataType: 'JSON',
    contentType: 'application/json',
    success: function(response) {
      location.reload();
    },
    error: function(response, status, err) {
      const msg = {
        response: response,
        status: status,
        error: err
      };
      console.log(`failed: ${JSON.stringify(msg, null, 2)}`);
    }
  });
}


function _page_data() {
  return {
    bookid: $("#book_id").val(),
    pagenum: $("#page_num").val()
  };
}

function delete_current_page() {
  if (!confirm("Delete current page?"))
    return;
  const d = _page_data()
  window.location = `/read/delete_page/${d.bookid}/${d.pagenum}`;
}

function _add_page(position) {
  const d = _page_data()
  window.location = `/read/new_page/${d.bookid}/${position}/${d.pagenum}`;
}

function add_page_before() {
  _add_page("before");
}

function add_page_after() {
  _add_page("after");
}


function handle_keydown (e) {
  if ($('span.word').length == 0) {
    // console.log('no words, exiting');
    return; // Nothing to do.
  }

  // Map of key codes (e.which) to lambdas:
  let map = {};

  const kESC = 27;
  const kRETURN = 13;
  const kLEFT = 37;
  const kRIGHT = 39;
  const kUP = 38;
  const kDOWN = 40;
  const kC = 67; // C)opy
  const kT = 84; // T)ranslate
  const kM = 77; // The(M)e
  const kH = 72; // Toggle H)ighlight
  const kF = 70; // Toggle F)ocus mode
  const k1 = 49;
  const k2 = 50;
  const k3 = 51;
  const k4 = 52;
  const k5 = 53;
  const kI = 73;
  const kW = 87;

  map[kESC] = () => start_hover_mode();
  map[kRETURN] = () => start_hover_mode();

  // read/index.js has some data rendered at the top of the page.
  const lang_is_rtl = $('#lang_is_rtl');
  let left_increment = -1;
  let right_increment = 1;
  if (lang_is_rtl == null)
    console.log("ERROR: missing lang control.");
  else {
    const is_rtl = (lang_is_rtl.val().toLowerCase() == "true");
    if (is_rtl) {
      left_increment = 1;
      right_increment = -1;
    }
  }

  map[kLEFT] = () => move_cursor(left_increment);
  map[kRIGHT] = () => move_cursor(right_increment);
  map[kUP] = () => increment_status_for_selected_elements(e, +1);
  map[kDOWN] = () => increment_status_for_selected_elements(e, -1);
  map[kC] = () => handle_copy(e);
  map[kT] = () => show_sentence_translation(e);
  map[kM] = () => next_theme();
  map[kH] = () => toggle_highlight();
  map[kF] = () => toggleFocus();
  map[k1] = () => update_status_for_marked_elements(1);
  map[k2] = () => update_status_for_marked_elements(2);
  map[k3] = () => update_status_for_marked_elements(3);
  map[k4] = () => update_status_for_marked_elements(4);
  map[k5] = () => update_status_for_marked_elements(5);
  map[kI] = () => update_status_for_marked_elements(98);
  map[kW] = () => update_status_for_marked_elements(99);

  if (e.which in map) {
    let a = map[e.which];
    a();
  }
  else {
    // console.log('unhandled key ' + e.which);
  }
}


/**
 * If the term editing form is visible when reading, and a hotkey is hit,
 * the form status should also update.
 */
function update_term_form(el, new_status) {
  const sel = 'input[name="status"][value="' + new_status + '"]';
  var radioButton = top.frames.wordframe.document.querySelector(sel);
  if (radioButton) {
    radioButton.click();
  }
  else {
    // Not found - user might just be hovering over the element,
    // or multiple elements selected.
    // console.log("Radio button with value " + new_status + " not found.");
  }
}


function update_status_for_marked_elements(new_status) {
  let elements = $('span.kwordmarked').toArray().concat($('span.wordhover').toArray());
  let updates = [ make_status_update_hash(new_status, elements) ]
  post_bulk_update(updates);
}


function make_status_update_hash(new_status, elements) {
  const texts = elements.map(el => $(el).text());
  return {
    new_status: new_status,
    terms: texts
  }
}


function post_bulk_update(updates) {
  if (updates.length == 0) {
    // console.log("No updates.");
    return;
  }
  let elements = $('span.kwordmarked').toArray().concat($('span.wordhover').toArray());
  if (elements.length == 0)
    return;
  const firstel = $(elements[0]);
  const first_status = updates[0].new_status;
  const langid = firstel.data('lang-id');
  const selected_ids = $('span.kwordmarked').toArray().map(el => $(el).attr('id'));

  data = JSON.stringify({
    langid: langid, updates: updates
  });

  let re_mark_selected_ids = function() {
    for (let i = 0; i < selected_ids.length; i++) {
      let el = $(`#${selected_ids[i]}`);
      el.addClass('kwordmarked');
    }
    if (selected_ids.length > 0)
      $('span.wordhover').removeClass('wordhover');
  };

  let reload_text_div = function() {
    const bookid = $('#book_id').val();
    const pagenum = $('#page_num').val();
    const url = `/read/renderpage/${bookid}/${pagenum}`;
    const repel = $('#thetext');
    repel.load(url, re_mark_selected_ids);
  };

  $.ajax({
    url: '/term/bulk_update_status',
    type: 'post',
    data: data,
    dataType: 'JSON',
    contentType: 'application/json',
    success: function(response) {
      reload_text_div();
      if (elements.length == 1) {
        update_term_form(firstel, first_status);
      }
    },
    error: function(response, status, err) {
      const msg = {
        response: response,
        status: status,
        error: err
      };
      console.log(`failed: ${JSON.stringify(msg, null, 2)}`);
    }
  });

}


/**
 * Change status using arrow keys for selected or hovered elements.
 */
function increment_status_for_selected_elements(e, shiftBy) {
  // Don't scroll screen.  If screen scrolling happens, then pressing
  // "up" will both scroll up *and* change the status the selected term,
  // which is odd.
  e.preventDefault();

  const elements = Array.from(document.querySelectorAll('span.kwordmarked, span.wordhover'));
  if (elements.length == 0)
    return;

  const statuses = ['status0', 'status1', 'status2', 'status3', 'status4', 'status5', 'status99'];

  // Build payloads to update for each unique status that will be changing
  let status_elements = statuses.reduce((obj, status) => {
    obj[status] = [];
    return obj;
  }, {});

  elements.forEach((element) => {
    let s = element.dataset.statusClass ?? 'missing';
    if (s in status_elements)
      status_elements[s].push(element);
  });

  // Convert map to update hashes.
  let updates = []

  Object.entries(status_elements).forEach(([status, update_elements]) => {
    if (update_elements.length == 0)
      return;

    let status_index = statuses.indexOf(status);
    let new_index = status_index + shiftBy;
    new_index = Math.max(0, Math.min((statuses.length-1), new_index));
    let new_status = Number(statuses[new_index].replace(/\D/g, ''));

    // Can't set status to 0 (that is for deleted/non-existent terms only).
    // TODO delete term from reading screen: setting to 0 could equal deleting term.
    if (new_index != status_index && new_status != 0) {
      updates.push(make_status_update_hash(new_status, update_elements));
    }
  });

  post_bulk_update(updates);
}
