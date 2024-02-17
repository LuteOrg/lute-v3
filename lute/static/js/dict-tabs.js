"use strict";

/**
 * A "dictionary button" to be shown in the UI.
 * Manages display state, loading and caching content.
 *
 * The class *could* be broken up into things like
 * PopupDictButton, EmbeddedDictButton, etc, but no need for that yet.
 */
class DictButton {

  /** All DictButtons created. */
  static all_buttons = [];

  constructor(dictURL, frameName) {
    let createIFrame = function(name) {
      const f = document.createElement("iframe");
      f.name = name;
      f.src = "about:blank";
      f.classList.add("dictframe");
      return f;
    };

    this.dictID = null;
    this.is_active = false;
    this.contentLoaded = false;

    this.frame = createIFrame(frameName);
    this.btn = document.createElement("button");
    this.btn.classList.add("dict-btn");

    DictButton.all_buttons.push(this);

    // Some DictButtons aren't actually dicts, e.g. Sentence tab and
    // Image button.  Perhaps there's a better class design ...
    if (dictURL == null) {
      return;
    }

    this.dictID = TERM_DICTS.indexOf(dictURL);
    if (this.dictID == -1) {
      console.log(`Error: Dict url ${dictURL} not found (??)`);
      return;
    }

    const url = dictURL.split("*").splice(-1)[0];

    this.label = (url.length <= 10) ? url : (url.slice(0, 10) + '...');

    // If the URL is a real url, get icon and label.
    try {
      const urlObj = new URL(url);  // Throws if invalid.
      const domain = urlObj.hostname;
      this.label = domain.split("www.").splice(-1)[0];

      const fimg = document.createElement("img");
      fimg.classList.add("dict-btn-fav-img");
      const favicon_src = `http://www.google.com/s2/favicons?domain=${domain}`;
      fimg.src = favicon_src;
      this.btn.prepend(fimg);
    }
    catch(err) {}

    this.btn.textContent = this.label;
    this.btn.setAttribute("title", this.label);

    this.isExternal = (dictURL.charAt(0) == '*');
    if (this.isExternal) {
      const ext_img = document.createElement("img");
      ext_img.classList.add("dict-btn-external-img");
      this.btn.appendChild(ext_img);
    }

    this.btn.onclick = () => this.do_lookup();
  }

  /** LOOKUPS *************************/

  do_lookup() {
    const dicturl = TERM_DICTS[this.dictID];
    const term = TERM_FORM_CONTAINER.querySelector("#text").value;
    if (this.isExternal) {
      this._load_popup(dicturl, term);
    }
    else {
      this._load_frame(dicturl, term);
      this.activate();
    }
  }

  _get_lookup_url(dicturl, term) {
    let ret = dicturl;
    // Terms are saved with zero-width space between each token;
    // remove that for dict searches.
    const zeroWidthSpace = '\u200b';
    const sqlZWS = '%E2%80%8B';
    const cleantext = term.
          replaceAll(zeroWidthSpace, '').
          replace(/\s+/g, ' ');
    const searchterm = encodeURIComponent(cleantext).
          replaceAll(sqlZWS, '');
    ret = ret.replace('###', searchterm);
    return ret;
  }

  _load_popup(url, term) {
    if ((url ?? "") == "")
      return;
    if (url[0] == "*")  // Should be true!
      url = url.slice(1);
    const lookup_url = this._get_lookup_url(url, term);
    window.open(
      lookup_url,
      'otherwin',
      'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no'
    );
  }

  _load_frame(dicturl, text) {
    if (this.isExternal || this.dictID == null) {
      return;
    }
    if (this.contentLoaded) {
      console.log(`${this.label} content already loaded.`);
      return;
    }

    let url = this._get_lookup_url(dicturl, text);

    const is_bing = (dicturl.indexOf('www.bing.com') != -1);
    if (is_bing) {
      // TODO handle_image_lookup_separately: don't mix term lookups with image lookups.
      let use_text = text;
      const binghash = dicturl.replace('https://www.bing.com/images/search?', '');
      url = `/bing/search/${LANG_ID}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
    }

    this.frame.setAttribute("src", url);
    this.contentLoaded = true;
  }

  /** Activate/deact. *************************/

  deactivate() {
    this.is_active = false;
    this.btn.classList.remove("dict-btn-active");
    this.frame.classList.remove("dict-active");
  }

  activate() {
    DictButton.all_buttons.forEach(tab => tab.deactivate());
    this.is_active = true;
    this.btn.classList.add("dict-btn-active");
    this.frame.classList.add("dict-active");
  }

}


/** Factory method for sentence, image buttons. */
let _make_standalone_tab = function(
  btn_id, framename,
  btn_textContent, btn_title, btn_className,
  clickHandler
) {
  const tab = new DictButton(null, framename);
  const b = tab.btn;
  b.setAttribute("id", btn_id);
  b.setAttribute("title", btn_title);
  b.textContent = btn_textContent;
  b.classList.add(btn_className);
  b.addEventListener("click", function () {
    if (!tab.contentLoaded) {
      clickHandler(tab.frame);
    }
    tab.contentLoaded = true;
    tab.activate();
  });
  return tab;
}


/**
 * Load excess buttons in a separate div.
 */
function _create_dict_dropdown_div(buttons_in_list) {
  // div containing all the buttons_in_list.
  const list_div = document.createElement("div");
  list_div.setAttribute("id", "dict-list-container");
  list_div.classList.add("dict-list-hide");
  buttons_in_list.forEach(tab => {
    tab.btn.classList.remove("dict-btn");
    tab.btn.classList.add("dict-menu-item");
    list_div.appendChild(tab.btn);
  });

  // Top level button to show/hide the list.
  const btn = document.createElement("button");
  btn.classList.add("dict-btn", "dict-btn-select");
  btn.innerHTML = "&hellip; &#9660;"
  btn.setAttribute("title", "More dictionaries");
  btn.addEventListener("click", (e) => {
    list_div.classList.toggle("dict-list-hide");
  });

  const menu_div = document.createElement("div");
  menu_div.setAttribute("id", "dict-menu-container");
  menu_div.appendChild(list_div);
  menu_div.appendChild(btn);
  menu_div.addEventListener("mouseleave", () => {
    list_div.classList.add("dict-list-hide");
  });

  return menu_div;
}

/**
 * Create dictionary tabs, and a listing for any extra dicts.
 */
function createDictButtons(tab_count = 5) {
  let destroy_existing_dictTab_controls = function() {
    document.querySelectorAll(".dict-btn").forEach(item => item.remove())
    document.querySelectorAll(".dictframe").forEach(item => item.remove())
    const el = document.getElementById("dict-menu-container");
    if (el)
      el.remove();
  }
  destroy_existing_dictTab_controls();
  DictButton.all_buttons = [];

  if (TERM_DICTS.length <= 0) return;

  const dev_hack_add_dicts = Array.from({ length: 8 }, (_, i) => `a${i}`);
  TERM_DICTS.push(...dev_hack_add_dicts);

  TERM_DICTS.forEach((dict, index) => {
    const tab = new DictButton(dict,`dict${index}`);
  });

  let buttons_in_tabs = DictButton.all_buttons.slice(0, tab_count);
  let buttons_in_list = DictButton.all_buttons.slice(tab_count);

  if (buttons_in_list.length == 1) {
    // Don't bother making a list with a single item.
    buttons_in_tabs = DictButton.all_buttons;
    buttons_in_list = [];
  }

  const layout_container = document.getElementById("dicttabslayout");
  const grid_column_count = buttons_in_tabs.length + (buttons_in_list.length > 0 ? 1 : 0);
  layout_container.style.gridTemplateColumns = `repeat(${grid_column_count}, minmax(2rem, 8rem))`;

  buttons_in_tabs.forEach(tab => layout_container.appendChild(tab.btn));
  if (buttons_in_list.length > 0) {
    const m = _create_dict_dropdown_div(buttons_in_list);
    layout_container.appendChild(m);
  }
  
  // Set first embedded frame as active.
  const active_tab = DictButton.all_buttons.find(tab => !tab.isExternal);
  if (active_tab)
    active_tab.activate();

  const sentence_tab = _make_standalone_tab(
    "sentences-btn", "sentencesframe",
    "Sentences", "See term usage", "dict-sentences-btn", do_sentence_lookup);

  const image_tab = _make_standalone_tab(
    "dict-image-btn", "imageframe",
    null, "Lookup images", "dict-image-btn", do_image_lookup);

  for (let tab of Object.values([sentence_tab, image_tab])) {
    document.getElementById("dicttabsstatic").appendChild(tab.btn);
  }

  const dictframes = document.getElementById("dictframes");
  DictButton.all_buttons.forEach((tab) => { dictframes.appendChild(tab.frame); });
}


function loadDictionaries() {
  const dictContainer = document.querySelector(".dictcontainer");
  dictContainer.style.display = "flex";
  dictContainer.style.flexDirection = "column";

  DictButton.all_buttons.forEach(tab => tab.contentLoaded = false);
  const active_tab = DictButton.all_buttons.find(tab => tab.is_active && !tab.isExternal);
  if (active_tab)
    active_tab.do_lookup();
}


function do_sentence_lookup(iframe) {
  const txt = TERM_FORM_CONTAINER.querySelector("#text").value;
  // %E2%80%8B is the zero-width string.  The term is reparsed
  // on the server, so this doesn't need to be sent.
  const t = encodeURIComponent(txt).replaceAll('%E2%80%8B', '');
  if (LANG_ID == '0' || t == '')
    return;
  iframe.setAttribute("src", `/term/sentences/${LANG_ID}/${t}`);
}


function do_image_lookup(iframe) {
  const text = TERM_FORM_CONTAINER.querySelector("#text").value;
  if (LANG_ID == null || LANG_ID == '' || parseInt(LANG_ID) == 0 || text == null || text == '') {
    alert('Please select a language and enter the term.');
    return;
  }
  let use_text = text;

  // If there is a single parent, use that as the basis of the lookup.
  const parents = get_parents();
  if (parents.length == 1)
    use_text = parents[0];

  const raw_bing_url = 'https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle';
  const binghash = raw_bing_url.replace('https://www.bing.com/images/search?', '');
  const url = `/bing/search/${LANG_ID}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;

  iframe.setAttribute("src", url);
}

/** Parents are in the tagify-managed #parentslist input box. */
let get_parents = function() {
  // During form load, and in "steady state" (i.e., after the tags
  // have been added or removed, and the focus has switched to
  // another control) the #sync_status text box is loaded with the
  // values.
  const pdata = $('#parentslist').val();
  if ((pdata ?? '') == '') {
    return [];
  }
  const j = JSON.parse(pdata);
  const parents = j.map(e => e.value);
  return parents;
};
