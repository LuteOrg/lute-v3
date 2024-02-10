"use strict";

function createDictTabs(num = 0) {
  // TERM_DICTS.push("*https://glosbe.com/de/en/###");
  // TERM_DICTS.push("*https://en.langenscheidt.com/german-english/###");
  // TERM_DICTS.push("*https://en.pons.com/translate/german-english/###");
  // TERM_DICTS.push("*https://www.collinsdictionary.com/dictionary/german-english/###");
  // TERM_DICTS.push("https://de.thefreedictionary.com/###");
  // TERM_DICTS.push("*https://dict.tu-chemnitz.de/deutsch-englisch/###.html");
  // TERM_DICTS.push("*https://www.translate.ru/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4/%D0%BD%D0%B5%D0%BC%D0%B5%D1%86%D0%BA%D0%B8%D0%B9-%D0%B0%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9/###");

  if (TERM_DICTS.length <= 0) return;

  let sliceIndex;
  let columnCount;

  if (num < 0) num = 0;

  if (num == 0 || num == null || num >= TERM_DICTS.length) {
    sliceIndex = TERM_DICTS.length;
    columnCount = sliceIndex;
  } else {
    sliceIndex = num - 1;
    columnCount = num;
  }
  
  const TABBED_DICTS = TERM_DICTS.slice(0, sliceIndex);
  const LISTED_DICTS = TERM_DICTS.slice(sliceIndex);

  const dictTabButtons = new Map();
  const dictTabsContainer = document.getElementById("dicttabs");
  const dictTabsLayoutContainer = document.getElementById("dicttabslayout");
  const iFramesContainer = document.getElementById("dictframes");
  
  dictTabsLayoutContainer.style.gridTemplateColumns = `repeat(${columnCount}, minmax(2rem, 8rem))`;

  TABBED_DICTS.forEach((dict, index) => {
    const domain = getDictURLDomain(dict);
    const faviconURL = getFavicon(domain);
    let iFrame = null;
    let btnLabel = domain.split("www.").splice(-1)[0];

    const btn = createTabBtn(btnLabel, 
                              dictTabsLayoutContainer, 
                              index, 
                              isURLExternal(dict), 
                              faviconURL);

    if (!isURLExternal(dict)) {
      iFrame = createIFrame(`dict${index}`, iFramesContainer);
    }
    
    dictTabButtons.set(btn, iFrame);
  });

  if (LISTED_DICTS.length > 0) {
    let iFrame = null;
    const isAllExternal = LISTED_DICTS.every(dict => isURLExternal(dict));
    if (!isAllExternal) {
      iFrame = createIFrame("listframe", iFramesContainer);
    }
   
    const domain = getDictURLDomain(LISTED_DICTS[0]);
    const faviconURL = getFavicon(domain);
    const btn = createTabBtn(domain.split("www.").splice(-1)[0], 
                              dictTabsLayoutContainer, 
                              TERM_DICTS.indexOf(LISTED_DICTS[0]), 
                              isURLExternal(LISTED_DICTS[0]), 
                              faviconURL);
    btn.setAttribute("title", "Right click for dictionary list");
    const menuImgEl = createImg("", "dict-btn-list-img");
    btn.appendChild(menuImgEl);
    btn.classList.add("dict-btn-select");
    
    dictTabButtons.set(btn, iFrame);
    
    const listMenuContainer = createDictListMenu(LISTED_DICTS);

    const selectButtonBox = document.createElement("div");
    // selectList.setAttribute("id", "dict-select");
    selectButtonBox.setAttribute("id", "select-btn-box");
    selectButtonBox.appendChild(btn); // add select AFTER button
    selectButtonBox.appendChild(listMenuContainer); // add select AFTER button
    dictTabsLayoutContainer.appendChild(selectButtonBox);

    // EVENTS
    btn.addEventListener("contextmenu", (e) => {
      e.preventDefault(); // disables default right click menu
      listMenuContainer.classList.toggle("dict-select-list-hide");
    });

    btn.addEventListener("click", (e) => {
      if (e.target === menuImgEl) return;
      listMenuContainer.classList.add("dict-select-list-hide");
    });

    menuImgEl.addEventListener("click", (e) => {
      e.stopPropagation();
      listMenuContainer.classList.toggle("dict-select-list-hide");
    });

    selectButtonBox.addEventListener("mouseleave", () => {
      listMenuContainer.classList.add("dict-select-list-hide");
    });

    listMenuContainer.addEventListener("click", (e) => {
      listMenuClick(e, listMenuContainer, btn, dictTabButtons, iFrame);
    });
  }
  
  // set first embedded frame as active
  const tabsArray = Array.from(dictTabButtons.keys());
  const framesArray = Array.from(dictTabButtons.values());

  framesArray.forEach(frame => {if (frame) frame.dataset.tabOpened = 0;});

  const firstEmbeddedTab = tabsArray.find(tab => tab.dataset.dictExternal == 0);
  if (firstEmbeddedTab) {
      const firstEmbeddedFrame = dictTabButtons.get(firstEmbeddedTab);
      firstEmbeddedTab.classList.add("dict-btn-active");
      firstEmbeddedTab.dataset.firstEmbedded = 1;
      firstEmbeddedFrame.dataset.tabOpened = 1;
      firstEmbeddedFrame.classList.add("dict-active");
  }

  // create image button
  const imageBtn = createTabBtn("", dictTabsContainer, -1, 0);
  imageBtn.setAttribute("id", "dict-image-btn");
  imageBtn.setAttribute("title", "Look up images for the term");
  const imageFrame = createIFrame("imageframe", iFramesContainer);

  dictTabButtons.set(imageBtn, imageFrame);
  // create sentences frame
  const sentencesFrame = createIFrame("sentencesframe", iFramesContainer);
  dictTabButtons.set("sentencesTab", sentencesFrame);

  dictTabsContainer.addEventListener("click", (e) => {
    tabsClick(e, dictTabButtons);
  });

  return dictTabButtons;
}

function tabsClick(event, dictTabButtons) {
  const clickedTab = event.target.closest(".dict-btn");
  if (!clickedTab) return;

  const isExternal = clickedTab.dataset.dictExternal == 1 ? true : false;
  const dictID = clickedTab.dataset.dictId;

  if (isExternal) {
    loadDictPage(dictID, "");
  } else {
    const iFrame = dictTabButtons.get(clickedTab);
    if (iFrame.dataset.tabOpened == 0) {
      loadDictPage(dictID, iFrame);
    }
    iFrame.dataset.tabOpened = 1;
    activateTab(clickedTab, dictTabButtons);
  }
}

function listMenuClick(event, listMenuContainer, btn, dictTabButtons, iFrame) {
  const clickedOption = event.target.closest(".dict-select-option");
  if (!clickedOption) return;

  listMenuContainer.classList.add("dict-select-list-hide");

  const optionVal = clickedOption.dataset.dictId;
  const domain = getDictURLDomain(TERM_DICTS[optionVal]);
  const btnLabel = domain.split("www.").splice(-1)[0];
  const faviconURL = getFavicon(domain);
  const faviconEl = createImg(faviconURL, "dict-btn-fav-img"); // img elements get deleted after "change" event. so we create them after each change
  
  btn.dataset.dictId = optionVal;
  btn.dataset.dictExternal = clickedOption.dataset.dictExternal;
  btn.textContent = btnLabel;
  // btn.dataset.tabOpened = clickedOption.dataset.tabOpened;
  btn.prepend(faviconEl);
  const menuImgEl = createImg("", "dict-btn-list-img");
  btn.appendChild(menuImgEl);
  
  if (clickedOption.dataset.dictExternal == 1) {
    loadDictPage(optionVal, "");

    const arrowEl = createImg("", "dict-btn-external-img");
    btn.appendChild(arrowEl);
    // btn.classList.remove("dict-btn-active");
  } else {
    loadDictPage(optionVal, iFrame);
    activateTab(btn, dictTabButtons);
  }
  // as with the icons, btn content changes so events get deleted
  menuImgEl.addEventListener("click", (e) => {
    e.stopPropagation();
    listMenuContainer.classList.toggle("dict-select-list-hide");
  });
}

function createDictListMenu(dicts) {
  const listContainer = document.createElement("div");
  listContainer.setAttribute("id", "dict-select-container");
  listContainer.classList.add("dict-select-list-hide");
  
  dicts.forEach((dict) => {
    const menuItem = document.createElement("p");
    menuItem.classList.add("dict-select-option");
    const origIndex = TERM_DICTS.indexOf(dict);
    const domain = getDictURLDomain(dict);
    const faviconURL = getFavicon(domain);
    const faviconEl = createImg(faviconURL, "dict-btn-fav-img");
    menuItem.textContent = domain.split("www.").splice(-1)[0];
    menuItem.prepend(faviconEl);
    menuItem.dataset.dictId = origIndex;
    menuItem.dataset.dictExternal = isURLExternal(dict) ? 1 : 0;
    listContainer.appendChild(menuItem);
  });

  return listContainer;
}

function loadDictionaries(dictTabButtons) {
  dictTabButtons.forEach((iframe, btn) => {
    if (iframe) iframe.dataset.tabOpened = 0;
  });
  // dictContainer needs to be defined here and not retrieved from global var because it's in different pages
  const dictContainer = document.querySelector(".dictcontainer");
  dictContainer.style.display = "flex";
  dictContainer.style.flexDirection = "column";

  const activeTab = document.querySelector(".dict-btn-active");
  const activeFrame = document.querySelector(".dict-active");

  if (activeFrame) {
    if (activeTab) {
      const dictID = activeTab.dataset.dictId;
      loadDictPage(dictID, activeFrame);
    } else {
      if (activeFrame.getAttribute("name") == "sentencesframe") {
        const url = getSentenceURL();
        activeFrame.setAttribute("src", url);
        activateTab("sentencesTab", dictTabButtons);
      }
    }
    activeFrame.dataset.tabOpened = 1;
  }
}

function addSentenceBtnEvent(dictTabButtons) {
  const iframe = dictTabButtons.get("sentencesTab");
  const sentencesBtn = TERM_FORM_CONTAINER.querySelector("#term-button-container > a");

  sentencesBtn.addEventListener("click", (e) => {
    e.preventDefault();

    const url = getSentenceURL();
    if (!url) return;
    
    if (iframe.dataset.tabOpened == 0) {
      iframe.setAttribute("src", url);
    }
    
    activateTab("sentencesTab", dictTabButtons);
    iframe.dataset.tabOpened = 1;
    iframe.classList.add("dict-active");
  });
}

function getSentenceURL() {
  const txt = TERM_FORM_CONTAINER.querySelector("#text").value;
  // check for the "new term" page
  if (txt.length == 0) return;
  // %E2%80%8B is the zero-width string.  The term is reparsed
  // on the server, so this doesn't need to be sent.
  const t = encodeURIComponent(txt).replaceAll('%E2%80%8B', '');
  if (LANG_ID == '0' || t == '')
    return;

  const url = `/term/sentences/${LANG_ID}/${t}`;

  return url;
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

function loadDictPage(dictID, iFrame) {
  //const iFrameName = iFrame.getAttribute("name") ? iFrame : "";
  const term = TERM_FORM_CONTAINER.querySelector("#text").value;

  if (dictID == -1) {
    do_image_lookup(term, iFrame);
  } else {
    const dict = TERM_DICTS[dictID];
    show_lookup_page(dict, term, iFrame);
  }
}

function createIFrame(name, parent) {
  const iFrame = document.createElement("iframe");
  iFrame.name = name;
  iFrame.src = "about:blank";
  iFrame.classList.add("dictframe");

  parent.appendChild(iFrame);

  return iFrame;
}

function createTabBtn(label, parent, data, external, faviconURL=null) {
  const btn = document.createElement("button");
  if (label) {
    btn.textContent = label;
    btn.setAttribute("title", label);
  }
  if (data != null) btn.dataset.dictId = data;
  if (external != null) {
    btn.dataset.dictExternal = external ? 1 : 0;
    if (external) {
      const arrowEl = createImg("", "dict-btn-external-img");
      btn.appendChild(arrowEl);
    }
  }

  btn.classList.add("dict-btn");

  if (faviconURL) {
    const faviconEl = createImg(faviconURL, "dict-btn-fav-img");
    btn.prepend(faviconEl);
  }
  
  parent.appendChild(btn);

  return btn;
}

function createImg(src, className) {
  const img = document.createElement("img");
  img.classList.add(className);
  if (src) img.src = src;

  return img;
}

function isURLExternal(dictURL) {
  return (dictURL.charAt(0) == '*') ? true : false; 
}

function getDictURLDomain(url) {
  const cleanURLString = url.split("*").splice(-1)[0];
  const urlObj = new URL(cleanURLString);

  return urlObj.hostname;
}

function getFavicon(domain) {
  return `http://www.google.com/s2/favicons?domain=${domain}`;
}

/**
   * Either open a new window, or show the result in the correct frame.
   */
function show_lookup_page(dicturl, text, iframe) {
  // if iframe is provided use that, else it's an external link

  const is_bing = (dicturl.indexOf('www.bing.com') != -1);
  if (is_bing) {
    let use_text = text;
    const binghash = dicturl.replace('https://www.bing.com/images/search?', '');
    const url = `/bing/search/${LANG_ID}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
    document.querySelector(`[name="${iframe}"]`).setAttribute("src", url);
    return;
  }

  if (iframe) {
    const url = get_lookup_url(dicturl, text);
    iframe.setAttribute("src", url);
  } else {
    // TODO zzfuture fix: fix_language_dict_asterisk
    // The URL shouldn not be prepended with trash
    // (e.g. "*http://" means "open an external window", while
    // "http://" means "this can be opened in an iframe."
    // Instead, each dict should have an "is_external" property.
    dicturl = dicturl.slice(1);
    const url = get_lookup_url(dicturl, text);
    openPopupWindow(url);
  }
}

function openPopupWindow(url) {
  window.open(
    url,
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