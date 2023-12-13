/* Lute functions. */

/**
 * The current term index (either clicked or hovered over)
 */
let LUTE_CURR_TERM_DATA_ORDER = -1;  // initially not set.

/**
 * Lute has 2 different "modes" when reading:
 * - LUTE_HOVERING = true: Hover mode, not selecting
 * - LUTE_HOVERING = false: Word clicked, or click-drag
 */ 
let LUTE_HOVERING = true;

/**
 * When the reading pane is first loaded, it is set in "hover mode",
 * meaning that when the user hovers over a word, that word becomes
 * the "active word" -- i.e., status update keyboard shortcuts should
 * operate on that hovered word, and as the user moves the mouse
 * around, the "active word" changes.  When a word is clicked, though,
 * there can't be any "hover changes", because the user should be
 * editing the word in the Term edit pane, and has to consciously
 * disable the "clicked word" mode by hitting ESC or RETURN.
 *
 * When the user is done editing a the Term form in the Term edit pane
 * and hits "save", the main reading page's text div is updated (see
 * templates/read/updated.twig.html).  This text div reload then has
 * to notify _this_ javascript to start_hover_mode() again.
 * 
 * I dislike this code (specifically, that the updated.twig.html calls
 * this javascript function), but can't think of a better way to
 * manage this.
 */
function start_hover_mode(should_clear_frames = true) {
  // console.log('CALLING RESET');
  load_reading_pane_globals();
  LUTE_HOVERING = true;

  $('span.kwordmarked').removeClass('kwordmarked');

  const w = get_current_word();
  if (w != null) {
    $(w).addClass('wordhover');
    apply_status_class($(w));
  }

  if (should_clear_frames)
    clear_frames();

  clear_newmultiterm_elements();

  // https://stackoverflow.com/questions/35022716/keydown-not-detected-until-window-is-clicked
  $(window).focus();
}

let clear_frames = function() {
  $('#wordframeid').attr('src', '/read/empty');
  $('#dictframeid').attr('src', '/read/empty');
}


/** 
 * Prepare the interaction events with the text.
 */
function prepareTextInteractions(textid) {
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
  }

  $(document).on('keydown', handle_keydown);

  $('#thetext').tooltip({
    position: { my: 'left top+10', at: 'left bottom', collision: 'flipfit flip' },
    items: '.word.showtooltip',
    show: { easing: 'easeOutCirc' },
    content: function (setContent) { tooltip_textitem_hover_content($(this), setContent); }
  });
}


/**
 * Build the html content for jquery-ui tooltip.
 */
let tooltip_textitem_hover_content = function (el, setContent) {
  elid = parseInt(el.attr('data_wid'));
  $.ajax({
    url: `/read/termpopup/${elid}`,
    type: 'get',
    success: function(response) {
      setContent(response);
    }
  });
}


function showEditFrame(el, extra_args = {}) {
  const lid = parseInt(el.attr('lid'));

  let text = extra_args.textparts ?? [ el.attr('data_text') ];
  const sendtext = text.join('');

  let extras = Object.entries(extra_args).
      map((p) => `${p[0]}=${encodeURIComponent(p[1])}`).
      join('&');

  const url = `/read/termform/${lid}/${sendtext}?${extras}`;
  // console.log('go to url = ' + url);

  top.frames.wordframe.location.href = url;
}


let save_curr_data_order = function(el) {
  LUTE_CURR_TERM_DATA_ORDER = parseInt(el.attr('data_order'));
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
 * Terms have data_status_class attribute.  If highlights should be shown,
 * then add that value to the actual span. */
function add_status_classes() {
  if (!_show_highlights())
    return;
  $('span.word').toArray().forEach(function (w) {
    apply_status_class($(w));
  });
}

/** Add the data_status_class to the term's classes. */
let apply_status_class = function(el) {
  el.addClass(el.attr("data_status_class"));
}

/** Remove the status from elements, if not showing highlights. */
let remove_status_highlights = function() {
  if (_show_highlights()) {
    /* Not removing anything, always showing highlights. */
    return;
  }
  $('span.word').toArray().forEach(function (m) {
    el = $(m);
    el.removeClass(el.attr("data_status_class"));
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
  if (! LUTE_HOVERING)
    return;
  $('span.wordhover').removeClass('wordhover');
  $(this).addClass('wordhover');
  save_curr_data_order($(this));
}

function hover_out(e) {
  if (! LUTE_HOVERING)
    return;
  $('span.wordhover').removeClass('wordhover');
}


/* ========================================= */
/** Multiword selection */

let selection_start_el = null;

let clear_newmultiterm_elements = function() {
  $('.newmultiterm').removeClass('newmultiterm');
  selection_start_el = null;
}

function select_started(e) {
  LUTE_HOVERING = false;
  $('span.wordhover').removeClass('wordhover');
  clear_newmultiterm_elements();
  clear_frames();
  $(this).addClass('newmultiterm');
  selection_start_el = $(this);
  save_curr_data_order($(this));
}

let get_selected_in_range = function(start_el, end_el, selector) {
  const first = parseInt(start_el.attr('data_order'))
  const last = parseInt(end_el.attr('data_order'));

  let startord = first;
  let endord = last;

  if (startord > endord) {
    endord = first;
    startord = last;
  }

  const selected = $(selector).filter(function() {
    const ord = $(this).attr("data_order");
    return ord >= startord && ord <= endord;
  });
  return selected;
};

function select_over(e) {
  if (selection_start_el == null)
    return;  // Not selecting
  $('.newmultiterm').removeClass('newmultiterm');
  const selected = get_selected_in_range(selection_start_el, $(this), 'span.textitem');
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

  const selected = get_selected_in_range(selection_start_el, $(this), 'span.textitem');
  if (e.shiftKey) {
    copy_text_to_clipboard(selected.toArray());
    start_hover_mode(false);
    return;
  }

  const textparts = selected.toArray().map((el) => $(el).text());
  const text = textparts.join('').trim();
  if (text.length > 250) {
    alert(`Selections can be max length 250 chars ("${text}" is ${text.length} chars)`);
    start_hover_mode();
    return;
  }

  showEditFrame(selection_start_el, { textparts: textparts });
  selection_start_el = null;
}


let word_clicked = function(el, e) {
  el.removeClass('wordhover');
  save_curr_data_order(el);
  if (el.hasClass('kwordmarked')) {
    el.removeClass('kwordmarked');
    const nothing_marked = $('span.kwordmarked').length == 0;
    if (nothing_marked) {
      el.addClass('wordhover');
      start_hover_mode();
    }
  }
  else {
    if (! e.shiftKey) {
      $('span.kwordmarked').removeClass('kwordmarked');
      showEditFrame(el);
    }
    el.addClass('kwordmarked');
    el.removeClass('hasflash');
  }
}


/********************************************/
// Keyboard navigation.

// Load all words into scope.
var words = null;
var maxindex = null;

function load_reading_pane_globals() {
  words = $('span.word').sort(function(a, b) {
    return $(a).attr('data_order') - $(b).attr('data_order');
  });
  // console.log('have ' + words.size() + ' words');
  maxindex = words.size() - 1;
}

$(document).ready(load_reading_pane_globals);

let current_word_index = function() {
  const i = words.toArray().findIndex(x => parseInt(x.getAttribute('data_order')) === LUTE_CURR_TERM_DATA_ORDER);
  // console.log(`found index = ${i}`);
  return i;
};

let get_current_word = function() {
  const selindex = current_word_index();
  if (selindex == -1)
    return null;
  return words.eq(selindex);
}

/** Get the rest of the textitems in the current active/hovered word's
 * sentence or paragraph, or null if no selection. */
let get_textitems_spans = function(e) {
  const w = get_current_word();
  if (w == null)
    return null;

  let attr_name = 'seid';
  let attr_value = w.attr('seid');

  if (e.shiftKey) {
    attr_name = 'paraid';
    attr_value = w.attr('paraid');
  }

  return $('span.textitem').toArray().filter(x => x.getAttribute(attr_name) === attr_value);
};

/** Copy the text of the textitemspans to the clipboard, and add a
 * color flash. */
let handle_copy = function(e) {
  tis = get_textitems_spans(e);
  if (tis == null)
    return;
  copy_text_to_clipboard(tis);
}

let copy_text_to_clipboard = function(textitemspans, show_flash = true) {
  const copytext = textitemspans.map(s => $(s).text()).join('');

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


let set_cursor = function(newindex) {
  LUTE_HOVERING = false;
  $('span.wordhover').removeClass('wordhover');
  clear_newmultiterm_elements();

  if (newindex < 0 || newindex >= words.size())
    return;
  let curr = words.eq(newindex);
  save_curr_data_order(curr);
  remove_status_highlights();
  $('span.kwordmarked').removeClass('kwordmarked');
  curr.addClass('kwordmarked');
  apply_status_class(curr);
  $(window).scrollTo(curr, { axis: 'y', offset: -150 });
  showEditFrame(curr, { autofocus: false });
}


let find_non_Ign_or_Wkn = function(currindex, shiftby) {
  let newindex = currindex + shiftby;
  while (newindex >= 0 && newindex <= maxindex) {
    const nextword = words.eq(newindex);
    const st = nextword.attr('data_status_class');
    if (st != 'status99' && st != 'status98') {
      break;
    }
    newindex += shiftby;
  }
  return newindex;
};

let move_cursor = function(shiftby, e) {
  const currindex = current_word_index();
  if (! e.shiftKey) {
    set_cursor(currindex + shiftby);
  }
  else {
    set_cursor(find_non_Ign_or_Wkn(currindex, shiftby));
  }
}


let show_translation = function(e) {
  tis = get_textitems_spans(e);
  if (tis == null)
    return;
  const sentence = tis.map(s => $(s).text()).join('');
  // console.log(sentence);

  const userdict = $('#translateURL').text();
  if (userdict == null || userdict == '')
    console.log('No userdict for lookup.  ???');

  // console.log(userdict);
  const url = userdict.replace('###', encodeURIComponent(sentence));
  if (url[0] == '*') {
    const finalurl = url.substring(1);  // drop first char.
    const settings = 'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no';
    window.open(finalurl, 'dictwin', settings);
  }
  else {
    top.frames.dictframe.location.href = url;
  }
}


/* Change to the next theme, and reload the page. */
let next_theme = function(e) {
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


/* Toggle highlighting, and reload the page. */
let toggle_highlight = function(e) {
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


function handle_keydown (e) {
  if (words.size() == 0) {
    // console.log('no words, exiting');
    return; // Nothing to do.
  }

  // Map of key codes (e.which) to lambdas:
  let map = {};

  const kESC = 27;
  const kRETURN = 13;
  const kHOME = 36;
  const kEND = 35;
  const kLEFT = 37;
  const kRIGHT = 39;
  const kUP = 38;
  const kDOWN = 40;
  const kC = 67; // C)opy
  const kT = 84; // T)ranslate
  const kM = 77; // The(M)e
  const kH = 72; // Toggle H)ighlight
  const k1 = 49;
  const k2 = 50;
  const k3 = 51;
  const k4 = 52;
  const k5 = 53;
  const kI = 73;
  const kW = 87;

  map[kESC] = () => start_hover_mode();
  map[kRETURN] = () => start_hover_mode();
  map[kHOME] = () => set_cursor(0);
  map[kEND] = () => set_cursor(maxindex);
  map[kLEFT] = () => move_cursor(-1, e);
  map[kRIGHT] = () => move_cursor(+1, e);
  map[kUP] = () => increment_status_for_marked_elements(+1);
  map[kDOWN] = () => increment_status_for_marked_elements(-1);
  map[kC] = () => handle_copy(e);
  map[kT] = () => show_translation(e);
  map[kM] = () => next_theme(e);
  map[kH] = () => toggle_highlight(e);
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
 * post update ajax call, fix the UI.
 */
function update_selected_statuses(newStatus, elements) {
  if (!elements) {
    console.error('Expecting argument `elements` to exist');
    return;
  }
  const newClass = `status${newStatus}`;
  let update_data_status_class = function (e) {
    const curr = $(this);
    ltext = curr.text().toLowerCase();
    matches = $('span.word').toArray().filter(el => $(el).text().toLowerCase() == ltext);
    matches.forEach(function (m) {
      $(m).removeClass('status98 status99 status0 status1 status2 status3 status4 status5 shiftClicked')
        .addClass(newClass)
        .attr('data_status_class',`${newClass}`);
    });
  };
  $(elements).each(update_data_status_class)
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
  update_status_for_elements(new_status, elements);
}

function update_status_for_elements(new_status, elements) {
  if (elements.length == 0)
    return;
  const firstel = $(elements[0]);
  const langid = firstel.attr('lid');
  const texts = elements.map(el => $(el).text());

  data = JSON.stringify({
    langid: langid,
    terms: texts,
    new_status: new_status
  });

  $.ajax({
    url: '/term/bulk_update_status',
    type: 'post',
    data: data,
    dataType: 'JSON',
    contentType: 'application/json',
    success: function(response) {
      update_selected_statuses(new_status, elements);
      if (texts.length == 1) {
        update_term_form(firstel, new_status);
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

function increment_status_for_marked_elements(shiftBy) {
  const validStatuses = ['status0', 'status1', 'status2', 'status3', 'status4', 'status5', 'status99'];
  const elements = Array.from(document.querySelectorAll('span.kwordmarked, span.wordhover'));

  // Build payloads to update for each unique status that will be changing
  let payloads = {};

  elements.forEach((element) => {
    let statusClass = element.getAttribute('data_status_class');
    
    if (!statusClass || !validStatuses.includes(statusClass)) return;

    payloads[statusClass] ||= [];
    payloads[statusClass].push(element);
  })

  Object.keys(payloads).forEach((key) => {
    let originalIndex = validStatuses.indexOf(key);

    if (originalIndex == -1) return;
    
    newIndex = Math.max(0, Math.min((validStatuses.length-1), originalIndex+shiftBy));

    if (newIndex != originalIndex) {
      const newStatusCode = Number(validStatuses[newIndex].replace(/\D/g, ''));

      // Can't set status to 0, that implies term deletion, which is a different issue
      // (at the moment).
      // TODO delete term from reading screen: setting to 0 could equal deleting term.
      if (newStatusCode != 0) {
        update_status_for_elements(newStatusCode, payloads[key]);
      }
    }
  })
}
