/* Lute functions. */

/**
 * The current term index (either clicked or hovered over)
 */
let LUTE_CURR_TERM_DATA_ORDER = -1;  // initially not set.


/**
 * Reset the cursor.
 *
 * When read/page_content.html is rendered, the current
 * cursor styling etc is wiped off the screen, so it needs
 * to be restored.
 */
function reset_cursor_marker() {
  $('span.kwordmarked').removeClass('kwordmarked');

  const curr_word = $('span.word').filter(function() {
    return _get_order($(this)) == LUTE_CURR_TERM_DATA_ORDER;
  });
  if (curr_word.length == 1) {
    const w = $(curr_word[0]);
    $(w).addClass('wordhover');
    apply_status_class($(w));
  }

  // Refocus on window so keyboard events work.
  // ref https://stackoverflow.com/questions/35022716
  $(window).focus();
}


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
function start_hover_mode() {
  reset_cursor_marker();
  _hide_term_edit_form();
  _hide_dictionaries();
  clear_newmultiterm_elements();
}

/* ========================================= */
/** Interactions. */


/* User can explicitly set the screen type from the reading_menu. (templates/read/reading_menu) */
function set_screen_type(screen_type) {
  localStorage.setItem("screen_interactions_type", screen_type);
  window.location.reload();
}

/**
 * Find if on mobile.
 *
 * This appears to still be a big hassle.  Various posts
 * say to not use the userAgent sniffing, and use feature tests
 * instead.
 * ref: https://stackoverflow.com/questions/72502079/
 *   how-can-i-check-if-the-device-which-is-using-my-website-is-a-mobile-user-or-no
 * From the above, using answer from marc_s: https://stackoverflow.com/a/76055222/1695066
 *
 * The various answers posted are still incorrect in certain cases,
 * so Lute users can set the screen_interactions_type for the session.
 */
const _isUserUsingMobile = () => {
  const s = localStorage.getItem('screen_interactions_type');
  if (s == 'desktop')
    return false;
  if (s == 'mobile')
    return true;

  // User agent string method
  let isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  // Screen resolution method.
  // Using the same arbitrary width check (980) as used
  // by the various window.matchMedia checks elsewhere in the code.
  // The original method in the SO post had width, height < 768,
  // but that broke playwright tests which opens a smaller browser window.
  if (!isMobile) {
    isMobile = (window.screen < 980);
  }

  // Disabling this check - see https://stackoverflow.com/a/4819886/1695066
  // for the many cases where this fails.
  // Touch events method
  // if (!isMobile) {
  //   isMobile = (('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0));
  //  }

  // CSS media queries method
  if (!isMobile) {
    let bodyElement = document.getElementsByTagName('body')[0];
    isMobile = window.getComputedStyle(bodyElement).getPropertyValue('content').indexOf('mobile') !== -1;
  }

  return isMobile
}


/** 
 * Prepare the interaction events with the text.
 */
function prepareTextInteractions() {
  if (_isUserUsingMobile()) {
    console.log('Using mobile interactions');
    _add_mobile_interactions();
  }
  else {
    console.log('Using desktop interactions');
    _add_desktop_interactions();
  }

  $(document).on('keydown', handle_keydown);

  $('#thetext').tooltip({
    position: _get_tooltip_pos(),
    items: '.word',
    show: { easing: 'easeOutCirc' },
    content: function (setContent) { tooltip_textitem_hover_content($(this), setContent); }
  });
}


function _add_mobile_interactions() {
  const t = $('#thetext');
  t.on('touchstart', '.word', touch_started);
  t.on('touchend', '.word', touch_ended);
}


function _add_desktop_interactions() {
  const t = $('#thetext');
  // Using "t.on" here because .word elements
  // are added and removed dynamically, and "t.on"
  // ensures that events remain for each element.
  t.on('mousedown', '.word', handle_select_started);
  t.on('mouseover', '.word', handle_select_over);
  t.on('mouseup', '.word', handle_select_ended);
  t.on('mouseover', '.word', hover_over);
  t.on('mouseout', '.word', hover_out);
  if (!_show_highlights()) {
    t.on('mouseover', '.word', hover_over_add_status_class);
    t.on('mouseout', '.word', remove_status_highlights);
  }
}

/* ========================================= */
/** Tooltip (term detail hover). */

let _get_tooltip_pos = function() {
  let ret = {my: 'left top+10', at: 'left bottom', collision: 'flipfit flip'};
  if (window.matchMedia("(max-width: 980px)").matches) {
    ret = {my: 'center bottom', at: 'center top-10', collision: 'flipfit flip'};
  }
  return ret;
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


/* ========================================= */
/** Showing the edit form. */

function _show_wordframe_url(url) {
  top.frames.wordframe.location.href = url;
  applyInitialPaneSizes();  // in resize.js
}

function show_term_edit_form(el) {
  const wid = parseInt(el.data('wid'));
  _show_wordframe_url(`/read/edit_term/${wid}`);
}

function show_bulk_term_edit_form(count_of_terms) {
  const url = '/read/term_bulk_edit_form';

  const wordFrame = top.frames.wordframe;

  function updateSpanContent() {
    const frameDocument = wordFrame.document;
    const spanElement = $(frameDocument).find('#bulkUpdateCount');
    if (spanElement.length) {
      spanElement.text(`Updating ${count_of_terms} term(s)`);
    }
  }

  if (!wordFrame.location.href.endsWith(url))
    wordFrame.location.href = url;
  else
    updateSpanContent();
}

function _hide_dictionaries() {
  $('.dictcontainer').hide();
}

/* Hide word editing form. */
function _hide_term_edit_form() {
  $('#wordframeid').attr('src', '/read/empty');
  // NOTE: checking for specific URLs or fragments in the location.href
  // causes security errors in some cases.
  /*
  const hide_me = ['read/edit_term', 'read/term_bulk_edit_form', 'read/termform'];
  const c = top.frames.wordframe.location.href;
  if (hide_me.some(path => c.includes(path))) {
    $('#wordframeid').attr('src', '/read/empty');
  }
  */
}

function show_multiword_term_edit_form(selected) {
  if (selected.length == 0)
    return;
  const textparts = selected.toArray().map((el) => $(el).text());
  const text = textparts.join('').trim();
  if (text == "")
    return;
  const lid = parseInt(selected.eq(0).data('lang-id'));
  // "/" in the term cause problems with routing, so hack a fix.
  const sendtext = text.replace(/\//g, "LUTESLASH");
  _show_wordframe_url(`/read/termform/${lid}/${sendtext}`);
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
  el.toggleClass('kwordmarked');

  // If Shift isn't held, this is a regular click.
  if (! e.shiftKey) {
    // No other elements should be marked clicked.
    $('span.kwordmarked').not(el).removeClass('kwordmarked');
    if (el.hasClass('kwordmarked')) {
      el.removeClass('hasflash');
      show_term_edit_form(el);
    }
    else {
      _hide_dictionaries();
      _hide_term_edit_form();
    }
    return;
  }

  // Shift is held ... have 0 or more elements clicked.
  const count_marked = $('span.kwordmarked').length;
  if (count_marked == 0) {
    el.addClass('wordhover');
    start_hover_mode();
  }
  else {
    _hide_dictionaries();
    show_bulk_term_edit_form(count_marked);
  }
}


/* ========================================= */
/** Multiword selection */

let selection_start_el = null;
let selection_start_shift_held = false;

let clear_newmultiterm_elements = function() {
  $('.newmultiterm').removeClass('newmultiterm');
  selection_start_el = null;
  selection_start_shift_held = false;
}

function handle_select_started(e) {
  select_started($(this), e);
}

function select_started(el, e) {
  clear_newmultiterm_elements();
  el.addClass('newmultiterm');
  selection_start_el = el;
  selection_start_shift_held = e.shiftKey;
  save_curr_data_order(el);
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

function handle_select_over(e) {
  select_over($(this), e);
}
  
function select_over(el, e) {
  if (selection_start_el == null)
    return;  // Not selecting
  $('.newmultiterm').removeClass('newmultiterm');
  const selected = get_selected_in_range(selection_start_el, el);
  selected.addClass('newmultiterm');
}

function handle_select_ended(e) {
  select_ended($(this), e);
}

function select_ended(el, e) {
  // Handle single word click.
  if (selection_start_el.attr('id') == el.attr('id')) {
    clear_newmultiterm_elements();
    word_clicked(el, e);
    return;
  }

  $('span.kwordmarked').removeClass('kwordmarked');

  const selected = get_selected_in_range(selection_start_el, el);
  if (selection_start_shift_held) {
    copy_text_to_clipboard(selected.toArray());
    clear_newmultiterm_elements();
    return;
  }

  show_multiword_term_edit_form(selected);
  selection_start_el = null;
  selection_start_shift_held = false;
}


/********************************************/
// Mobile events.
//
// 1. Regular vs long taps.
//
// Ref https://borstch.com/blog/javascript-touch-events-and-mobile-specific-considerations
//
// I had used https://github.com/benmajor/jQuery-Touch-Events, but
// during development was running into problems with chrome dev tool
// mobile emulation freezing.  I thought it was the library but the
// problem occurred with the vanilla js below.
//
// https://stackoverflow.com/questions/22722727/
// chrome-devtools-mobile-emulation-scroll-not-working suggests that
// it's a devtools problem, and I agree, as it occurred at random.
// I'm still sticking with the vanilla js below though: it's very
// simple, and there's no need to add another dependency just to
// distinguish regular and long taps.
//
// 2. Single tap vs double tap
//
// For my iphone at least, double-tap didn't seem to work, even though
// it did in chrome devtools emulation.  For my iphone, the phone
// browser seemed to add a delay after each click, so the double
// clicks were never fast enough to be distinguishable.  For that
// reason, instead of using click time differences to distinguish
// between single and double clicks, the code tracks the
// _last_touched_element: if the second tap is the same as the first,
// it's treated as a double tap, regardless of the duration.  This is
// fine for Lute since the first tap only opens the term pop-up.
//
// 3. Scroll/swipe
//
// Swipes have to be tracked because each swipe starts with a touch,
// which gets confused with the other events.  If the touch start and
// end differ by a threshold amount, assume the user is scrolling.

// Tracking if long tap.
let _touch_start_time;
const _long_touch_min_duration_ms = 500;

// Tracking if double-click.
let _last_touched_element_id = null;

// Tracking if swipe.
let _touch_start_coords = null;
const _swipe_min_threshold_pixels = 15;

function _get_coords(touch) {
  var touchX = touch.clientX;
  var touchY = touch.clientY;
  // console.log('X: ' + touchX + ', Y: ' + touchY);
  return [ touchX, touchY ];
}

function _swipe_distance(e) {
  const curr_coords = _get_coords(e.originalEvent.changedTouches[0]);
  const dX = curr_coords[0] - _touch_start_coords[0];
  const dY = curr_coords[1] - _touch_start_coords[1];
  return Math.sqrt((dX * dX) + (dY * dY));
}

function touch_started(e) {
  _touch_start_coords = _get_coords(e.originalEvent.touches[0]);
  _touch_start_time = Date.now();
}

function touch_ended(e) {
  if (_swipe_distance(e) >= _swipe_min_threshold_pixels) {
    // Do nothing else if this was a swipe.
    return;
  }

  // The touch_ended handler is attached with t.on in
  // prepareTextInteractions, so the clicked element is just
  // $(this).
  const el = $(this);
  const this_id = el.attr("id")

  $('span.kwordmarked').removeClass('kwordmarked');
  $('span.wordhover').removeClass('wordhover');

  const touch_duration = Date.now() - _touch_start_time;
  const is_long_touch = (touch_duration >= _long_touch_min_duration_ms);
  const is_double_click = (this_id === _last_touched_element_id);
  _last_touched_element_id = null;  // Already checked in is_double_click.

  if (is_long_touch) {
    _tap_hold(el, e);
  }
  else if (selection_start_el != null) {
    select_over(el, e);
    select_ended(el, e);
  }
  else if (is_double_click) {
    _double_tap(el);
  }
  else {
    _single_tap(el);
    _last_touched_element_id = this_id;
    el.addClass('kwordmarked');
  }
}


// Tap-holds define the start and end of a multi-word term.
function _tap_hold(el, e) {
  // console.log('hold tap');
  if (selection_start_el == null) {
    select_started(el, e);
    select_over(el, e);
  }
  else {
    select_over(el, e);
    select_ended(el, e);
  }
}

// Show the form.
function _double_tap(el, e) {
  // console.log('double tap');
  $(".ui-tooltip").css("display", "none");
  clear_newmultiterm_elements();
  show_term_edit_form(el);
}

function _single_tap(el, e) {
  // console.log('single tap');
  clear_newmultiterm_elements();
  const term_is_status_0 = (el.data("status-class") == "status0");
  if (term_is_status_0) {
    show_term_edit_form(el);
  }
}


/********************************************/
// Keyboard navigation.

/** Get the textitems whose span_attribute value matches that of the
 * current active/hovered word.  If span_attribute is null, return
 * all. */
let get_textitems_spans = function(span_attribute) {
  if (span_attribute == null)
    return $('span.textitem').toArray();

  let elements = $('span.kwordmarked, span.newmultiterm, span.wordhover');
  elements.sort((a, b) => _get_order($(a)) - _get_order($(b)));
  if (elements.length == 0)
    return elements;

  const attr_value = $(elements[0]).data(span_attribute);
  const selector = `span.textitem[data-${span_attribute}="${attr_value}"]`;
  return $(selector).toArray();
};

let handle_bookmark = function() {
  // Function defined in read/index.html ... yuck, need to reorganize this js code.
  // TODO javascript: reorganize, or make modules.
  add_bookmark();
}

let handle_edit_page = function() {
  // Function defined in read/index.html ... yuck, need to reorganize this js code.
  // TODO javascript: reorganize, or make modules.
  edit_current_page();
}

let handle_mark_read_hotkey = function() {
  // Function defined in read/index.html ... yuck, need to reorganize this js code.
  // TODO javascript: reorganize
  handle_page_done(false, 1);
}

let handle_mark_read_well_known_hotkey = function() {
  // Function defined in read/index.html ... yuck, need to reorganize this js code.
  // TODO javascript: reorganize
  handle_page_done(true, 1);
}

/** Copy the text of the textitemspans to the clipboard, and add a
 * color flash. */
let handle_copy = function(span_attribute) {
  tis = get_textitems_spans(span_attribute);
  copy_text_to_clipboard(tis);
}

/** Get the text from the text items, adding "\n" between paragraphs. */
let _get_textitems_text = function(textitemspans) {
  if (textitemspans.length == 0)
    return '';

  let _partition_by_paragraph_id = function(textitemspans) {
    const partitioned = {};
    $(textitemspans).each(function() {
      const pid = $(this).attr('data-paragraph-id');
      if (!partitioned[pid])
        partitioned[pid] = [];
      partitioned[pid].push(this);
    });
    return partitioned;
  };
  const paras = _partition_by_paragraph_id(textitemspans);
  const paratexts = Object.entries(paras).map(([pid, spans]) => {
    let ptext = spans.map(s => $(s).text()).join('');
    return ptext.replace(/\u200B/g, '');
  });
  return paratexts.join('\n').trim();
}


let _show_element_message_tooltip = function(element, message) {
  const el = $(element);
  el.attr('title', message);
  el.tooltip({
    show: { effect: "fadeIn", duration: 200 },
    hide: { effect: "fadeOut", duration: 200 }
  });
  el.tooltip("open");
  setTimeout(function() {
    el.tooltip("close");
    el.removeAttr('title');
  }, 1000);
};


let copy_text_to_clipboard = function(textitemspans) {
  const copytext = _get_textitems_text(textitemspans);
  if (copytext == '')
    return;

  var textArea = document.createElement("textarea");
  textArea.value = copytext;
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand("Copy");
  textArea.remove();

  const removeFlash = function() {
    $('span.flashtextcopy').addClass('wascopied'); // for acceptance testing.
    $('span.flashtextcopy').removeClass('flashtextcopy');
  };

  removeFlash();
  textitemspans.forEach(function (t) {
    $(t).addClass('flashtextcopy');
  });
  setTimeout(() => removeFlash(), 1000);

  _show_element_message_tooltip(textitemspans[textitemspans.length - 1], "Copied to clipboard.");
}


/** First selected/hovered element, or null if nothing. */
let _first_selected_element = function() {
  let elements = $('span.kwordmarked, span.newmultiterm, span.wordhover');
  if (elements.length == 0)
    return null;
  elements.sort((a, b) => _get_order($(a)) - _get_order($(b)));
  return elements[0];
};


/** Update cursor, clear prior cursors. */
let _update_screen_cursor = function(target) {
  $('span.newmultiterm, span.kwordmarked, span.wordhover').removeClass('newmultiterm kwordmarked wordhover');
  remove_status_highlights();
  target.addClass('kwordmarked');
  save_curr_data_order(target);
  apply_status_class(target);
  $(window).scrollTo(target, { axis: 'y', offset: -150 });
  show_term_edit_form(target);
};


/** Move to the next/prev candidate determined by the selector.
 * direction is 1 if moving "right", -1 if moving "left" -
 * note that these switch depending on if the language is right-to-left! */
let _move_cursor = function(selector, direction = 1) {
  const fe = _first_selected_element();
  const fe_order = (fe != null) ? _get_order($(fe)) : 0;
  let candidates = $(selector).toArray();
  let comparator = function(a, b) { return a > b };
  if (direction < 0) {
    candidates = candidates.reverse();
    comparator = function(a, b) { return a < b };
  }

  const match = candidates.find(el => comparator(_get_order($(el)), fe_order));
  if (match) {
    _update_screen_cursor($(match));

    // Highlight the word if we're jumping around a lot.
    if (selector != 'span.word') {
      const match_order = _get_order($(match));
      const match_class = `flash_${match_order}`;
      $(match).addClass(`flashtextcopy ${match_class}`);
      setTimeout(() => $(`.${match_class}`).removeClass(`flashtextcopy ${match_class}`), 1000);
    }
  }
};


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
  let url = userdict.replace('[LUTE]', lookup);
  url = url.replace('###', lookup);  // TODO remove_old_###_placeholder: remove
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
function handle_translate(span_attribute) {
  const tis = get_textitems_spans(span_attribute);
  const text = _get_textitems_text(tis);
  show_translation_for_text(text);
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


function _lang_is_left_to_right() {
  // read/index.js has some data rendered at the top of the page.
  const lang_is_rtl = $('#lang_is_rtl');
  if (!lang_is_rtl.length) {
    console.error("ERROR: missing lang control.");
    return true;  // fallback.
  }
  return (lang_is_rtl.val().toLowerCase() !== "true");
}


function handle_keydown (e) {
  if ($('span.word').length == 0) {
    return; // Nothing to do.
  }

  const hotkey_name = get_hotkey_name(e);
  if (hotkey_name == null)
    return;

  const next_incr = _lang_is_left_to_right() ? 1 : -1;
  const prev_incr = -1 * next_incr;

  // Map of shortcuts to lambdas:
  let map = {
    "hotkey_StartHover": () => start_hover_mode(),
    "hotkey_PrevWord": () => _move_cursor('span.word', prev_incr),
    "hotkey_NextWord": () => _move_cursor('span.word', next_incr),
    "hotkey_PrevUnknownWord": () => _move_cursor('span.word.status0', prev_incr),
    "hotkey_NextUnknownWord": () => _move_cursor('span.word.status0', next_incr),
    "hotkey_PrevSentence": () => _move_cursor('span.word.sentencestart', prev_incr),
    "hotkey_NextSentence": () => _move_cursor('span.word.sentencestart', next_incr),
    "hotkey_StatusUp": () => increment_status_for_selected_elements(+1),
    "hotkey_StatusDown": () => increment_status_for_selected_elements(-1),
    "hotkey_Bookmark": () => handle_bookmark(),
    "hotkey_CopySentence": () => handle_copy('sentence-id'),
    "hotkey_CopyPara": () => handle_copy('paragraph-id'),
    "hotkey_CopyPage": () => handle_copy(null),
    "hotkey_EditPage": () => handle_edit_page(),
    "hotkey_TranslateSentence": () => handle_translate('sentence-id'),
    "hotkey_TranslatePara": () => handle_translate('paragraph-id'),
    "hotkey_TranslatePage": () => handle_translate(null),
    "hotkey_NextTheme": () => next_theme(),
    "hotkey_ToggleHighlight": () => toggle_highlight(),
    "hotkey_ToggleFocus": () => toggleFocus(),
    "hotkey_Status1": () => update_status_for_marked_elements(1),
    "hotkey_Status2": () => update_status_for_marked_elements(2),
    "hotkey_Status3": () => update_status_for_marked_elements(3),
    "hotkey_Status4": () => update_status_for_marked_elements(4),
    "hotkey_Status5": () => update_status_for_marked_elements(5),
    "hotkey_StatusIgnore": () => update_status_for_marked_elements(98),
    "hotkey_StatusWellKnown": () => update_status_for_marked_elements(99),
    "hotkey_DeleteTerm": () => update_status_for_marked_elements(0),

    // Functions defined in read/index.html, or refer to them
    // TODO javascript_hotkeys: fix javascript sprawl
    "hotkey_MarkRead": () => handle_mark_read_hotkey(),
    "hotkey_MarkReadWellKnown": () => handle_mark_read_well_known_hotkey(),
    "hotkey_PreviousPage": () => goto_relative_page(-1),
    "hotkey_NextPage": () => goto_relative_page(1),
  }

  if (hotkey_name in map) {
    // Override any existing event - e.g., if "up" arrow is in the map,
    // don't scroll screen.
    e.preventDefault();
    map[hotkey_name]();
  }
  else {
    // console.log(`hotkey "${hotkey_name}" not found in map`);
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
  return {
    new_status: new_status,
    termids: elements.map(el => $(el).data('wid'))
  };
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
  const selected_ids = $('span.kwordmarked').toArray().map(el => $(el).attr('id'));

  data = JSON.stringify({ updates: updates });

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
    const url = `/read/refresh_page/${bookid}/${pagenum}`;
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
function increment_status_for_selected_elements(shiftBy) {
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
