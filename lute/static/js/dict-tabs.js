"use strict";

let dictTabs = [];

class DictTab {
  constructor(dict, frameName) {
    const dictInfo = dict ? getDictInfo(dict) : null;
    this.dictID = dictInfo ? dictInfo.id : null;

    this.frame = this.createIFrame(frameName);
    this.btn = document.createElement("button");
    this.btn.classList.add("dict-btn");

    if (this.dictID != null) {
      this.label = dictInfo.label;
      this.isExternal = dictInfo.isExternal;
      this.btn.dataset.dictId = this.dictID;
      this.btn.onclick = this.clickCallback.bind(this);
      this.btn.dataset.dictExternal = this.isExternal ? "true" : "false";
      
      if (this.label != "") {
        this.btn.textContent = this.label;
        this.btn.setAttribute("title", this.label);
      }

      if (dictInfo.faviconURL) {
        this.btn.prepend(createImg(dictInfo.faviconURL, "dict-btn-fav-img"));
      }

      if (this.isExternal) {
        this.btn.appendChild(createImg("", "dict-btn-external-img"));
      }
    }
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

/**
 * Create dictionary tabs, and a listing for any extra dicts.
 */
function createDictTabs(tab_count) {
  if (TERM_DICTS.length <= 0) return;

  // TEMP HACK
  for (let i = 0; i < 5; i++) {
    /*
    TERM_DICTS.push(TERM_DICTS[0]);
    TERM_DICTS.push(TERM_DICTS[1]);
    */
    TERM_DICTS.push(`http://a${i}.com?###`);
    TERM_DICTS.push(`http://b${i}.com?###`);
  }

  const dictTabsLayoutContainer = document.getElementById("dicttabslayout");
  const dictTabsStaticContainer = document.getElementById("dicttabsstatic");
  const iFramesContainer = document.getElementById("dictframes");

  const all_dict_buttons = [];
  TERM_DICTS.forEach((dict, index) => {
    const tab = new DictTab(dict,`dict${index}`);

    dictTabs.push(tab);
    all_dict_buttons.push(tab.btn);
    iFramesContainer.appendChild(tab.frame);
  });

  const n = Math.max(0, tab_count);
  let TABBED_BUTTONS = all_dict_buttons.slice(0, n);
  let LISTED_BUTTONS = all_dict_buttons.slice(n);

  // If the LISTED_BUTTONS only contains one item, just add it as
  // a tab, as it will take up the same space.
  if (LISTED_BUTTONS.length == 1) {
    TABBED_BUTTONS = all_dict_buttons;
    LISTED_BUTTONS = [];
  }

  const grid_column_count = TABBED_BUTTONS.length + (LISTED_BUTTONS.length > 0 ? 1 : 0);
  dictTabsLayoutContainer.style.gridTemplateColumns = `repeat(${grid_column_count}, minmax(2rem, 8rem))`;

  // console.log(TABBED_BUTTONS);
  for (const b of TABBED_BUTTONS) {
    // console.log(typeof b);
    // console.log(b);
    dictTabsLayoutContainer.appendChild(b);
  }
  // !CLICKING MENU ITEM DOES NOT UPDATE MAIN BUTTON LABEL AND IMAGES (FAVICON AND EXTERNAL)
  if (LISTED_BUTTONS.length > 0) {
    const first = LISTED_BUTTONS[0];
    const show_clone = first.cloneNode(true);  // deep copy.
    dictTabsLayoutContainer.appendChild(show_clone);
    show_clone.setAttribute("title", "Right click for dictionary list");
    const menuImgEl = createImg("", "dict-btn-list-img");
    show_clone.appendChild(menuImgEl);
    show_clone.classList.add("dict-btn-select");

    const list_div = document.createElement("div");
    list_div.setAttribute("id", "dict-list-container");
    list_div.classList.add("dict-list-hide");
    for (const b of LISTED_BUTTONS) {
      b.classList.remove("dict-btn");
      b.classList.add("dict-menu-item");
      list_div.appendChild(b);
    }

    const menu_div = document.createElement("div");
    menu_div.setAttribute("id", "dict-menu-container");
    menu_div.appendChild(list_div); // add select AFTER button
    menu_div.appendChild(show_clone);
    dictTabsLayoutContainer.appendChild(menu_div);

    // EVENTS
    show_clone.addEventListener("contextmenu", (e) => {
      e.preventDefault(); // disables default right click menu
      list_div.classList.toggle("dict-list-hide");
    });

    show_clone.addEventListener("click", (e) => {
      if (e.target === menuImgEl) return;
      list_div.classList.add("dict-list-hide");
    });

    menuImgEl.addEventListener("click", (e) => {
      e.stopPropagation();
      list_div.classList.toggle("dict-list-hide");
    });

    menu_div.addEventListener("mouseleave", () => {
      list_div.classList.add("dict-list-hide");
    });
  }
  
  // Set first embedded frame as active.
  const active_tab = dictTabs.find(tab => !tab.isExternal);
  if (active_tab) {
      active_tab.btn.classList.add("dict-btn-active");
      active_tab.frame.classList.add("dict-active");
  }
  
  // Sentences frame.
  const sentencesTab = new DictTab(null, "sentencesframe");
  dictTabsStaticContainer.appendChild(sentencesTab.btn);
  sentencesTab.btn.textContent = "Sentences";
  sentencesTab.btn.classList.add("dict-sentences-btn");
  iFramesContainer.appendChild(sentencesTab.frame);
  dictTabs.push(sentencesTab);

  // Image button and frame.
  const imageTab = new DictTab(null, "imageframe");
  imageTab.btn.setAttribute("id", "dict-image-btn");
  imageTab.btn.setAttribute("title", "Look up images for the term");
  dictTabsStaticContainer.appendChild(imageTab.btn);
  iFramesContainer.appendChild(imageTab.frame);
  dictTabs.push(imageTab);

  sentencesTab.btn.addEventListener("click", function () {
    if (sentencesTab.frame.dataset.contentLoaded == "false") {
      loadSentencesFrame(sentencesTab.frame);
    }
    activateTab(sentencesTab);
  });

  imageTab.btn.addEventListener("click", function () {
    if (imageTab.frame.dataset.contentLoaded == "false") {
      do_image_lookup(imageTab.frame);
    }
    activateTab(imageTab);
  });


  return dictTabs;
}

function loadSentencesFrame(iframe) {
  const url = getSentenceURL();
  if (url == null)
    return;
  iframe.setAttribute("src", url);
}

function loadDictionaries() {
  dictTabs.forEach(tab => tab.frame.dataset.contentLoaded = "false");
  const dictContainer = document.querySelector(".dictcontainer");
  dictContainer.style.display = "flex";
  dictContainer.style.flexDirection = "column";

  const activeFrame = document.querySelector(".dict-active");
  if (activeFrame == null)
    return;

  const activeTab = document.querySelector(".dict-btn-active");
  if (activeTab == null) 
    return;

  if ("dictId" in activeTab.dataset) {
    load_dict_iframe(activeTab.dataset.dictId, activeFrame);
  } else if (activeFrame.name === "imageframe") {
    do_image_lookup(activeFrame);
  } else if (activeFrame.name === "sentencesframe") {
    loadSentencesFrame(activeFrame);
  }

  activeFrame.dataset.contentLoaded = "true";
}

function getDictInfo(dictURL) {
  const cleanURL = dictURL.split("*").splice(-1)[0];

  let _getURLDomain = function(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch(err) {
      return null;
    }
  };

  let _getFavicon = function(domain) {
    if (domain)
      return `http://www.google.com/s2/favicons?domain=${domain}`;
    return null;
  };

  let _getLabel = function(domain, url) {
    if (domain)
      return domain.split("www.").splice(-1)[0]
    let label = url.slice(0, 10);
    if (label.length < url.length)
      label += '...';
    return label;
  }

  const domain = _getURLDomain(cleanURL);
  return {
    label: _getLabel(domain, cleanURL),
    isExternal: (dictURL.charAt(0) == '*') ? true : false,
    faviconURL: _getFavicon(domain),
    id: TERM_DICTS.indexOf(dictURL),
  };
}

function getSentenceURL() {
  const txt = TERM_FORM_CONTAINER.querySelector("#text").value;
  // check for the "new term" page
  if (txt.length == 0) return null;
  // %E2%80%8B is the zero-width string.  The term is reparsed
  // on the server, so this doesn't need to be sent.
  const t = encodeURIComponent(txt).replaceAll('%E2%80%8B', '');
  if (LANG_ID == '0' || t == '')
    return null;
  return `/term/sentences/${LANG_ID}/${t}`;
}

function activateTab(tab) {
  dictTabs.forEach(tab => {
    if (tab.btn.classList) tab.btn.classList.remove("dict-btn-active");
    if (tab.frame) tab.frame.classList.remove("dict-active");
  });

  const iFrame = tab.frame;
  if (tab.btn.classList) tab.btn.classList.add("dict-btn-active");
  if (iFrame) {
    iFrame.classList.add("dict-active");
    iFrame.dataset.contentLoaded = "true";
  }
}

function createImg(src, className) {
  const img = document.createElement("img");
  img.classList.add(className);
  if (src)
    img.src = src;
  return img;
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