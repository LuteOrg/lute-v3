/**
 * Tagify helpers.
 *
 * Lute uses Tagify (https://github.com/yairEO/tagify)
 * for parent terms and term tags.
 */


/**
 * Build a parent term tagify with autocomplete.
 *
 * args:
 * - input: the input box tagify will control
 * - language_id_func: zero-arg function that returns the language.
 *
 * notes:
 *
 * - language_id_func is passed, rather than a language_id, because in
 * some cases such as bulk term editing the language isn't known at
 * tagify setup time.  The func delegates the check until it's
 * actually needed, in _fetch_whitelist.
 */
function lute_tagify_utils_setup_parent_tagify(
  input,
  language_id_func,  // if returns null, autocomplete does nothing
  this_term_text = null,  // set to non-null to filter whitelist
  override_base_settings = {}
) {
  if (input._tagify) {
    // console.log('Tagify already initialized for this input.');
    return input._tagify;
  }

  // Do the fetch and build the whitelist.
  const _fetch_whitelist = function(mytagify, e_detail_value, controller) {
    const language_id = language_id_func();
    if (language_id == null) {
      console.log("language_id not set or not consistent");
      mytagify.loading(false);
      return;
    }

    // Create entry like "cat (a furry thing...)"
    const _make_dropdown_entry = function(hsh) {
      const txt = decodeURIComponent(hsh.text);
      let translation = hsh.translation ?? '';
      translation = translation.
        replaceAll("\n", "; ").
        replaceAll("\r", "").
        trim();
      if (translation == '')
        return txt;
      const max_translation_len = 40;
      if (translation.length > max_translation_len)
        translation = translation.slice(0, max_translation_len) + "...";
      translation = translation ? `(${translation})` : '';
      return [txt, translation].join(' ');
    };

    // Build whitelist from returned ajax data.
    const _build_whitelist = function(data) {
      const _make_hash = function(a) {
        return {
          "value": a.text,
          "id": a.id,
          "suggestion": _make_dropdown_entry(a),
          "status": a.status,
        };
      };
      return data.map((a) => _make_hash(a));
    };

    const encoded_value = encodeURIComponent(e_detail_value);
    const url = `/term/search/${encoded_value}/${language_id ?? -1}`;
    mytagify.loading(true);
    fetch(url, {signal:controller.signal})
      .then(RES => RES.json())
      .then(function(data) {
        // Update whitelist and render in place.
        let whitelist = _build_whitelist(data);
        whitelist = whitelist.filter(hsh => hsh.value != this_term_text);
        mytagify.whitelist = whitelist;
        mytagify.loading(false).dropdown.show(e_detail_value);
      }).catch(err => {
        if (err.name === 'AbortError') {
          // Do nothing, fetch was aborted due to another fetch.
          // console.log('AbortError: Fetch request aborted');
        }
        else {
          console.log(`error: ${err}`);
        }
        mytagify.loading(false);
      });
  };

  // Controller to handle cancellations/aborts of calls.
  // https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort
  var controller;

  // Build whitelist in response to user input.
  function build_autocomplete_dropdown(mytagify, e) {
    if (e.detail.value == '' || e.detail.value.length < 1) {
      controller && controller.abort();
      mytagify.whitelist = [];
      mytagify.loading(false).dropdown.hide();
      return;
    }
    controller && controller.abort()
    controller = new AbortController()
    _fetch_whitelist(mytagify, e.detail.value, controller);
  }

  // Need a global tagify instance here
  // so that hooks can use it.
  var tagify_instance = null;

  const make_Tagify_for = function(input) {
    const base_settings = {
      editTags: false,
      pasteAsTags: false,
      backspace: true,
      addTagOnBlur: true,   // note different
      autoComplete: { enabled: true, rightKey: true, tabKey: true },
      delimiters: ';;',  // special delimiter to handle parents with commas.
      enforceWhitelist: false,
      whitelist: [],
      dropdown: {
        enabled: 1,
        maxItems: 15,
        mapValueTo: 'suggestion',
        placeAbove: false,
      },
      templates: {
        dropdownFooter(suggestions) {
          var hasMore = suggestions.length - this.settings.dropdown.maxItems;
          if (hasMore <= 0)
            return '';
          return `<footer data-selector='tagify-suggestions-footer' class="${this.settings.classNames.dropdownFooter}">
        (more items available, please refine your search.)</footer>`;
        }
      },

      // Use a hook to force build_autocomplete_dropdown.
      // Pasting from the clipboard doesnt fire the
      // tagify.on('input') event, so intercept it and handle
      // it manually.
      hooks: {
        beforePaste : function(content) {
          return new Promise((resolve, reject) => {
            clipboardData = content.clipboardData || window.clipboardData;
            pastedData = clipboardData.getData('Text');
            let e = { detail: { value: pastedData } };
            build_autocomplete_dropdown(tagify_instance, e);
            resolve();
          });
        }
      },
    };

    let settings = { ...base_settings, ...override_base_settings };
    tagify_instance = new Tagify(input, settings);
    return tagify_instance;
  };

  const tagify = make_Tagify_for(input);
  tagify.on('input', function (e) {
    build_autocomplete_dropdown(tagify, e)
  });

  return tagify;
} // end lute_tagify_utils_setup_parent_tagify


/**
 * Build a term tag tagify with autocomplete.
 *
 * args:
 * - input: the input box tagify will control
 * - tags: the tags array
 * - override_base_settings: {} to override
 */
function lute_tagify_utils_setup_term_tag_tagify(
  input,
  tags,
  override_base_settings = {}
) {
  if (input._tagify) {
    return input._tagify;
  }

  const base_settings = {
    delimiters: ';;', // special delim to handle tags w/ commas
    editTags: false,
    autoComplete: { enabled: true, rightKey: true, tabKey: true },
    dropdown: { enabled: 1 },
    enforceWhitelist: false,
    whitelist: tags,
  };
  const settings = { ...base_settings, ...override_base_settings };
  const tagify = new Tagify(input, settings);
  return tagify;
} // end lute_tagify_utils_setup_term_tag_tagify
