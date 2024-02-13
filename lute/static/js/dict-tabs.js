"use strict";


function createTabBtn(label, dictID, external, faviconURL=null) {
  const btn = document.createElement("button");
  btn.classList.add("dict-btn");
  if (label != "") {
    btn.textContent = label;
    btn.setAttribute("title", label);
  }
  btn.dataset.dictId = dictID;
  btn.dataset.dictExternal = external ? "true" : "false";
  if (faviconURL)
    btn.prepend(createImg(faviconURL, "dict-btn-fav-img"));
  if (external)
    btn.appendChild(createImg("", "dict-btn-external-img"));
  return btn;
}


function createDictListMenu(dicts) {
  let _make_para = function (dict) {
    const dictInfo = getDictInfo(dict);
    const p = document.createElement("p");
    p.classList.add("dict-menu-item");
    p.textContent = dictInfo.label;
    p.dataset.dictId = TERM_DICTS.indexOf(dict);
    p.dataset.dictExternal = dictInfo.isExternal ? "true" : "false";
    p.dataset.contentLoaded = dictInfo.isExternal ? "false" : "true";
    if (dictInfo.faviconURL) {
      const faviconEl = createImg(dictInfo.faviconURL, "dict-btn-fav-img");
      p.prepend(faviconEl);
    }
    return p;
  };

  const paras = dicts.map(_make_para);

  const list_div = document.createElement("div");
  list_div.setAttribute("id", "dict-list-container");
  list_div.classList.add("dict-list-hide");
  for (let p of Object.values(paras)) {
    list_div.appendChild(p);
  }
  return list_div;
}


/**
 * Create dictionary tabs, and a listing for any extra dicts.
 */
function createDictTabs(tab_count) {
  if (TERM_DICTS.length <= 0) return;

  // TEMP HACK
  for (let i = 0; i < 5; i++) {
    TERM_DICTS.push(TERM_DICTS[0]);
    TERM_DICTS.push(TERM_DICTS[1]);
  }

  const dictTabButtons = new Map();
  const dictTabsContainer = document.getElementById("dicttabs");
  const dictTabsLayoutContainer = document.getElementById("dicttabslayout");
  const iFramesContainer = document.getElementById("dictframes");

  let createIFrame = function(name) {
    const f = document.createElement("iframe");
    f.name = name;
    f.src = "about:blank";
    f.classList.add("dictframe");
    f.dataset.contentLoaded = "false";
    iFramesContainer.appendChild(f);
    return f;
  }

  const n = Math.max(0, tab_count);
  let TABBED_DICTS = TERM_DICTS.slice(0, n);
  let LISTED_DICTS = TERM_DICTS.slice(n);

  // If the LISTED_DICTS only contains one item, just add it as
  // a tab, as it will take up the same space.
  if (LISTED_DICTS.length == 1) {
    TABBED_DICTS = TERM_DICTS;
    LISTED_DICTS = [];
  }

  const grid_column_count = TABBED_DICTS.length + (LISTED_DICTS.length > 0 ? 1 : 0);
  dictTabsLayoutContainer.style.gridTemplateColumns = `repeat(${grid_column_count}, minmax(2rem, 8rem))`;

  TABBED_DICTS.forEach((dict, index) => {
    const dictInfo = getDictInfo(dict);
    const tabBtn = createTabBtn(
      dictInfo.label,
      index, 
      dictInfo.isExternal, 
      dictInfo.faviconURL);
    dictTabsLayoutContainer.appendChild(tabBtn);
    let iFrame = dictInfo.isExternal ? null : createIFrame(`dict${index}`);
    dictTabButtons.set(tabBtn, iFrame);
  });


  if (LISTED_DICTS.length > 0) {
    const dictInfo = getDictInfo(LISTED_DICTS[0]);
    const tabBtn = createTabBtn(
      dictInfo.label, 
      TERM_DICTS.indexOf(LISTED_DICTS[0]), 
      dictInfo.isExternal, 
      dictInfo.faviconURL);
    dictTabsLayoutContainer.appendChild(tabBtn);
    tabBtn.setAttribute("title", "Right click for dictionary list");
    const menuImgEl = createImg("", "dict-btn-list-img");
    tabBtn.appendChild(menuImgEl);
    tabBtn.classList.add("dict-btn-select");

    let iFrame = null;
    const all_are_external = LISTED_DICTS.every(dict => getDictInfo(dict).isExternal);
    if (!all_are_external)
      iFrame = createIFrame("listframe");
    dictTabButtons.set(tabBtn, iFrame);
    
    const listMenuContainer = createDictListMenu(LISTED_DICTS);
    const menu_div = document.createElement("div");
    menu_div.setAttribute("id", "dict-menu-container");
    menu_div.appendChild(tabBtn); // add select AFTER button
    menu_div.appendChild(listMenuContainer); // add select AFTER button
    dictTabsLayoutContainer.appendChild(menu_div);

    // EVENTS
    tabBtn.addEventListener("contextmenu", (e) => {
      e.preventDefault(); // disables default right click menu
      listMenuContainer.classList.toggle("dict-list-hide");
    });

    tabBtn.addEventListener("click", (e) => {
      if (e.target === menuImgEl) return;
      listMenuContainer.classList.add("dict-list-hide");
    });

    menuImgEl.addEventListener("click", (e) => {
      e.stopPropagation();
      listMenuContainer.classList.toggle("dict-list-hide");
    });

    menu_div.addEventListener("mouseleave", () => {
      listMenuContainer.classList.add("dict-list-hide");
    });

    listMenuContainer.addEventListener("click", (e) => {
      listMenuClick(e, listMenuContainer, tabBtn, dictTabButtons, iFrame);
    });
  }
  
  // set first embedded frame as active
  const tabsArray = Array.from(dictTabButtons.keys());
  const firstEmbeddedTab = tabsArray.find(tab => tab.dataset.dictExternal == "false");
  if (firstEmbeddedTab) {
      firstEmbeddedTab.classList.add("dict-btn-active");
      const firstEmbeddedFrame = dictTabButtons.get(firstEmbeddedTab);
      firstEmbeddedFrame.dataset.contentLoaded = "true";
      firstEmbeddedFrame.classList.add("dict-active");
  }

  // Image button and frame.
  const imageBtn = createTabBtn("", -1, false);
  dictTabsContainer.appendChild(imageBtn);
  imageBtn.setAttribute("id", "dict-image-btn");
  imageBtn.setAttribute("title", "Look up images for the term");
  const imageFrame = createIFrame("imageframe");
  dictTabButtons.set(imageBtn, imageFrame);

  // Sentences frame.
  const sentencesFrame = createIFrame("sentencesframe");
  dictTabButtons.set("sentencesTab", sentencesFrame);

  // using onevent property to update the event listener later (formframes)
  dictTabsContainer.onclick = function(e) {
    const clickedTab = e.target.closest(".dict-btn");
    if (clickedTab)
      tabsClick(clickedTab, dictTabButtons);
  };

  return dictTabButtons;
}

function tabsClick(clickedTab, dictTabButtons) {
  const dictID = clickedTab.dataset.dictId;

  if (clickedTab.dataset.dictExternal == "true") {
    load_dict_popup(dictID);
    return;
  }

  const iFrame = dictTabButtons.get(clickedTab);
  if (iFrame.dataset.contentLoaded == "false") {
    load_dict_iframe(dictID, iFrame);
  }
  iFrame.dataset.contentLoaded = "true";
  activateTab(clickedTab, dictTabButtons);
}

function listMenuClick(event, listMenuContainer, menuBtn, dictTabButtons, iFrame) {
  const clickedItem = event.target.closest(".dict-menu-item");
  if (!clickedItem) return;
  listMenuContainer.classList.add("dict-list-hide");

  const dictID = clickedItem.dataset.dictId;
  const dictInfo = getDictInfo(TERM_DICTS[dictID]);
  menuBtn.dataset.dictId = dictID;
  menuBtn.dataset.dictExternal = clickedItem.dataset.dictExternal;
  menuBtn.dataset.contentLoaded = clickedItem.dataset.contentLoaded;
  menuBtn.textContent = dictInfo.label;

  if (dictInfo.faviconURL) {
    // img elements get deleted after "change" event, so create them after each change.
    const faviconEl = createImg(dictInfo.faviconURL, "dict-btn-fav-img");
    menuBtn.prepend(faviconEl);
  }

  const menuImgEl = createImg("", "dict-btn-list-img");
  menuImgEl.addEventListener("click", (e) => {
    e.stopPropagation();
    listMenuContainer.classList.toggle("dict-list-hide");
  });
  menuBtn.appendChild(menuImgEl);

  if (clickedItem.dataset.dictExternal == "true") {
    const arrowEl = createImg("", "dict-btn-external-img");
    menuBtn.appendChild(arrowEl);
  }

  if (clickedItem.dataset.dictExternal == "true") {
    load_dict_popup(dictID);
  }
  else {
    load_dict_iframe(dictID, iFrame);
    activateTab(menuBtn, dictTabButtons);
  }
}


function loadDictionaries(dictTabButtons) {
  dictTabButtons.forEach((iframe, btn) => {
    if (iframe) iframe.dataset.contentLoaded = "false";
  });
  const dictContainer = document.querySelector(".dictcontainer");
  dictContainer.style.display = "flex";
  dictContainer.style.flexDirection = "column";

  const activeFrame = document.querySelector(".dict-active");
  if (activeFrame == null)
    return;

  const activeTab = document.querySelector(".dict-btn-active");
  if (activeTab) {
    load_dict_iframe(activeTab.dataset.dictId, activeFrame);
  }
  else if (activeFrame.getAttribute("name") == "sentencesframe") {
    activeFrame.setAttribute("src", getSentenceURL());
    activateTab("sentencesTab", dictTabButtons);
  }
  activeFrame.dataset.contentLoaded = "true";
}

function addSentenceBtnEvent(dictTabButtons) {
  const b = TERM_FORM_CONTAINER.querySelector("#term-button-container > a");
  b.addEventListener("click", (e) => {
    e.preventDefault();
    const url = getSentenceURL();
    if (url == null)
      return;

    const iframe = dictTabButtons.get("sentencesTab");
    if (iframe.dataset.contentLoaded == "false") {
      iframe.setAttribute("src", url);
    }
    activateTab("sentencesTab", dictTabButtons);
    iframe.dataset.contentLoaded = "true";
    iframe.classList.add("dict-active");
  });
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

function activateTab(tab, allTabs) {
  allTabs.forEach((iframe, btn) => {
    if (btn.classList) btn.classList.remove("dict-btn-active");
    if (iframe) iframe.classList.remove("dict-active");
  });
  
  const iFrame = allTabs.get(tab);
  if (tab.classList) tab.classList.add("dict-btn-active");
  if (iFrame) iFrame.classList.add("dict-active");
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

  if (dictID == -1) {
    // TODO handle_image_lookup_separately: don't mix term lookups with image lookups.
    do_image_lookup(text, iframe);
    return;
  }

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

function do_image_lookup(text, iframe) {
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
