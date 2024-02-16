"use strict";

let dictTabs = [];


class DictTab {
  constructor(dictURL, frameName) {
    this.frame = this.createIFrame(frameName);
    this.btn = document.createElement("button");
    this.btn.classList.add("dict-btn");

    // Some DictTabs aren't actually dicts, e.g. Sentence tab and
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

    this.btn.dataset.dictId = this.dictID;
    this.btn.onclick = this.clickCallback.bind(this);
    this.btn.dataset.dictExternal = this.isExternal ? "true" : "false";
  }

  clickCallback() {
    if (this.isExternal) {
      load_dict_popup(this.dictID);
      return;
    }
    if (this.frame.dataset.contentLoaded == "false") {
      load_dict_iframe(this.dictID, this.frame);
    }

    activateTab(this);
  }

  createIFrame(name) {
    const f = document.createElement("iframe");
    f.name = name;
    f.src = "about:blank";
    f.classList.add("dictframe");
    f.dataset.contentLoaded = "false";

    return f;
  }

}


/** Factory method for sentence, image buttons. */
let _make_standalone_tab = function(
  btn_id, framename,
  btn_textContent, btn_title, btn_className,
  clickHandler
) {
  const tab = new DictTab(null, framename);
  const b = tab.btn;
  b.setAttribute("id", btn_id);
  b.setAttribute("title", btn_title);
  b.textContent = btn_textContent;
  b.classList.add(btn_className);
  b.addEventListener("click", function () {
    if (tab.frame.dataset.contentLoaded == "false") {
      clickHandler(tab.frame);
    }
    activateTab(tab);
  });
  return tab;
}


/**
 * Create dictionary tabs, and a listing for any extra dicts.
 */
function createDictTabs(tab_count = 5) {
  if (TERM_DICTS.length <= 0) return;

  const dictTabsLayoutContainer = document.getElementById("dicttabslayout");
  const dictTabsStaticContainer = document.getElementById("dicttabsstatic");
  const iFramesContainer = document.getElementById("dictframes");

  const allDictButtons = [];
  TERM_DICTS.forEach((dict, index) => {
    const tab = new DictTab(dict,`dict${index}`);

    dictTabs.push(tab);
    allDictButtons.push(tab.btn);
    iFramesContainer.appendChild(tab.frame);
  });

  const n = Math.max(0, tab_count);
  let buttons_in_tabs = allDictButtons.slice(0, n);
  let buttons_in_list = allDictButtons.slice(n);

  // If the buttons_in_list only contains one item, just add it as
  // a tab, as it will take up the same space.
  if (buttons_in_list.length == 1) {
    buttons_in_tabs = allDictButtons;
    buttons_in_list = [];
  }

  const grid_column_count = buttons_in_tabs.length + (buttons_in_list.length > 0 ? 1 : 0);
  dictTabsLayoutContainer.style.gridTemplateColumns = `repeat(${grid_column_count}, minmax(2rem, 8rem))`;

  buttons_in_tabs.forEach(btn => dictTabsLayoutContainer.appendChild(btn));
  
  if (buttons_in_list.length > 0) {
    // div containing all the buttons_in_list.
    const list_div = document.createElement("div");
    list_div.setAttribute("id", "dict-list-container");
    list_div.classList.add("dict-list-hide");
    buttons_in_list.forEach(btn => {
        btn.classList.remove("dict-btn");
        btn.classList.add("dict-menu-item");
        list_div.appendChild(btn);
      }
    );

    // Top level button to show/hide the list.
    const btn = document.createElement("button");
    btn.classList.add("dict-btn");
    btn.classList.add("dict-btn-select");
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

    dictTabsLayoutContainer.appendChild(menu_div);
  }
  
  // Set first embedded frame as active.
  const active_tab = dictTabs.find(tab => !tab.isExternal);
  if (active_tab) {
      active_tab.btn.classList.add("dict-btn-active");
      active_tab.frame.classList.add("dict-active");
  }

  const sentence_tab = _make_standalone_tab(
    "sentences-btn", "sentencesframe",
    "Sentences", "See term usage", "dict-sentences-btn", do_sentence_lookup);

  const image_tab = _make_standalone_tab(
    "dict-image-btn", "imageframe",
    null, "Lookup images", "dict-image-btn", do_image_lookup);

  for (let tab of Object.values([sentence_tab, image_tab])) {
    dictTabsStaticContainer.appendChild(tab.btn);
    iFramesContainer.appendChild(tab.frame);
    dictTabs.push(tab);
  }
}


function loadDictionaries() {
  dictTabs.forEach(tab => tab.frame.dataset.contentLoaded = "false");
  const dictContainer = document.querySelector(".dictcontainer");
  dictContainer.style.display = "flex";
  dictContainer.style.flexDirection = "column";

  const activeFrame = document.querySelector(".dict-active");
  const activeTab = document.querySelector(".dict-btn-active");
  if (activeFrame == null || activeTab == null)
    return;

  if ("dictId" in activeTab.dataset) {
    load_dict_iframe(activeTab.dataset.dictId, activeFrame);
    activeFrame.dataset.contentLoaded = "true";
  }
}


function activateTab(tab) {
  dictTabs.forEach(tab => {
    if (tab.btn.classList) tab.btn.classList.remove("dict-btn-active");
    if (tab.frame) tab.frame.classList.remove("dict-active");
  });

  if (tab.btn.classList)
    tab.btn.classList.add("dict-btn-active");
  if (tab.frame) {
    tab.frame.classList.add("dict-active");
    tab.frame.dataset.contentLoaded = "true";
  }
}

function load_dict_iframe(dictID, iframe) {
  const text = TERM_FORM_CONTAINER.querySelector("#text").value;
  const dicturl = TERM_DICTS[dictID];
  const is_bing = (dicturl.indexOf('www.bing.com') != -1);

  if (is_bing) {
    // TODO handle_image_lookup_separately: don't mix term lookups with image lookups.
    let use_text = text;
    const binghash = dicturl.replace('https://www.bing.com/images/search?', '');
    const url = `/bing/search/${LANG_ID}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
    iframe.setAttribute("src", url);
    return;
  }

  const url = get_lookup_url(dicturl, text);
  iframe.setAttribute("src", url);
}


function load_dict_popup(dictID) {
  let url = TERM_DICTS[dictID];
  if ((url ?? "") == "") {
    return;
  }
  if (url[0] == "*")  // Should be true!
    url = url.slice(1);
  const term = TERM_FORM_CONTAINER.querySelector("#text").value;
  const lookup_url = get_lookup_url(url, term);
  window.open(
    lookup_url,
    'otherwin',
    'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no'
  );
}


function get_lookup_url(dicturl, term) {
  let ret = dicturl;

  // Terms are saved with zero-width space between each token;
  // remove that for dict searches!
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

  return;
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
