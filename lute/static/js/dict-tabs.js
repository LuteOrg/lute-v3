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
      const favicon = `http://www.google.com/s2/favicons?domain=${domain}`;
      this.btn.prepend(createImg(favicon, "dict-btn-fav-img"));
    }
    catch(err) {}

    this.btn.textContent = this.label;
    this.btn.setAttribute("title", this.label);

    this.isExternal = (dictURL.charAt(0) == '*');
    if (this.isExternal)
      this.btn.appendChild(createImg("", "dict-btn-external-img"));

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

  const allDictButtons = [];
  TERM_DICTS.forEach((dict, index) => {
    const tab = new DictTab(dict,`dict${index}`);

    dictTabs.push(tab);
    allDictButtons.push(tab.btn);
    iFramesContainer.appendChild(tab.frame);
  });

  const n = Math.max(0, tab_count);
  let TABBED_BUTTONS = allDictButtons.slice(0, n);
  let LISTED_BUTTONS = allDictButtons.slice(n);

  // If the LISTED_BUTTONS only contains one item, just add it as
  // a tab, as it will take up the same space.
  if (LISTED_BUTTONS.length == 1) {
    TABBED_BUTTONS = allDictButtons;
    LISTED_BUTTONS = [];
  }

  const grid_column_count = TABBED_BUTTONS.length + (LISTED_BUTTONS.length > 0 ? 1 : 0);
  dictTabsLayoutContainer.style.gridTemplateColumns = `repeat(${grid_column_count}, minmax(2rem, 8rem))`;

  TABBED_BUTTONS.forEach(btn => dictTabsLayoutContainer.appendChild(btn));
  
  if (LISTED_BUTTONS.length > 0) {
    // div containing all the LISTED_BUTTONS.
    const list_div = document.createElement("div");
    list_div.setAttribute("id", "dict-list-container");
    list_div.classList.add("dict-list-hide");
    LISTED_BUTTONS.forEach(btn => {
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
  
  // Sentences frame.
  const sentencesTab = new DictTab(null, "sentencesframe");
  dictTabsStaticContainer.appendChild(sentencesTab.btn);
  // sentencesTab.btn.setAttribute("id", "sentences-btn");
  // sentencesTab.btn.setAttribute("title", "See term usage");
  sentencesTab.btn.textContent = "Sentences";
  sentencesTab.btn.classList.add("dict-sentences-btn");
  iFramesContainer.appendChild(sentencesTab.frame);
  sentencesTab.btn.addEventListener("click", function () {
    if (sentencesTab.frame.dataset.contentLoaded == "false") {
      loadSentencesFrame(sentencesTab.frame);
    }
    activateTab(sentencesTab);
  });

  dictTabs.push(sentencesTab);

  // Image button and frame.
  const imageTab = new DictTab(null, "imageframe");
  dictTabsStaticContainer.appendChild(imageTab.btn);
  imageTab.btn.setAttribute("id", "dict-image-btn");
  imageTab.btn.setAttribute("title", "Look up images for the term");
  imageTab.btn.textContent = null;
  imageTab.btn.classList.add("dict-image-btn");
  iFramesContainer.appendChild(imageTab.frame);
  imageTab.btn.addEventListener("click", function () {
    if (imageTab.frame.dataset.contentLoaded == "false") {
      do_image_lookup(imageTab.frame);
    }
    activateTab(imageTab);
  });

  dictTabs.push(imageTab);

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
