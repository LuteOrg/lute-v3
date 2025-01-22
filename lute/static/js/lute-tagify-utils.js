/**
 * Tagify helpers.
 *
 * Lute uses Tagify (https://github.com/yairEO/tagify)
 * for parent terms and term tags.
 */


/* /term/search used here:
  lute/templates/term/index.html
  lute/templates/term/_bulk_edit_form_fields.html
  lute/templates/term/_form.html
*/
function lute_tagify_utils_setup_parent_tagify(
  input,
  language_id = null,  // if null, autocomplete does nothing
  this_term_text = null,  // set to non-null to filter whitelist
  override_base_settings = {}
) {
  if (input._tagify) {
    // console.log('Tagify already initialized for this input.');
    return input._tagify;
  }

  // Do the fetch and build the whitelist.
  const _fetch_whitelist = function(mytagify, e_detail_value, controller) {
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
    const url = `/term/search/${encoded_value}/${language_id}`;
    mytagify.loading(true);
    fetch(url, {signal:controller.signal})
      .then(RES => RES.json())
      .then(function(data) {
        // Update whitelist and render in place.
        let whitelist = _build_whitelist(data);
        if (this_term_text != null)
          whitelist = whitelist.filter(hsh => hsh.text != this_term_text);
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
        maxItems: 10,
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
            // console.log("pasting => " + pastedData);
            let e = { detail: { value: pastedData } };
            build_autocomplete_dropdown(ret, e);
            resolve();
          });
        }
      },
    };

    let settings = { ...base_settings, ...override_base_settings };
    return new Tagify(input, settings);
  };

  const tagify = make_Tagify_for(input);
  tagify.on('input', function (e) {
    if (language_id == null) {
      console.log("language_id not set or not consistent");
      return;
    }
    build_autocomplete_dropdown(tagify, e)
  });

  return tagify;
} // end setup_parent_tagify
