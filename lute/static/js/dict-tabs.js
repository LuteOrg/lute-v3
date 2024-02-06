"use strict";

function createDictTabs(num = 0) {
  // TERM_DICTS.push("*https://glosbe.com/de/en/###");
  // TERM_DICTS.push("*https://en.langenscheidt.com/german-english/###");
  // TERM_DICTS.push("*https://en.pons.com/translate/german-english/###");
  // TERM_DICTS.push("*https://www.collinsdictionary.com/dictionary/german-english/###");
  // TERM_DICTS.push("*https://dict.tu-chemnitz.de/deutsch-englisch/###.html");

  let sliceIndex;
  let columnCount;

  if (num < 0) num = 0;
  if (num == 1) num = 2;

  if (num == 0 || num == null || num >= TERM_DICTS.length) {
    sliceIndex = TERM_DICTS.length;
    columnCount = sliceIndex;
  } else {
    sliceIndex = num - 1;
    columnCount = num;
  }
  
  const TABBED_DICTS = TERM_DICTS.slice(0, sliceIndex);
  const OPTION_DICTS = TERM_DICTS.slice(sliceIndex);

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

    if (isURLExternal(dict) == 0) {
      iFrame = createIFrame(`dict${index}`, iFramesContainer);
    }

    dictTabButtons.set(btn, iFrame);
  });

  if (OPTION_DICTS.length > 0) {
    const selectList = document.createElement("select");
    const selectButtonBox = document.createElement("div");
    const domain = getDictURLDomain(OPTION_DICTS[0]);
    const faviconURL = getFavicon(domain);
    const btn = createTabBtn(domain.split("www.").splice(-1)[0], 
                              selectButtonBox, 
                              TERM_DICTS.indexOf(OPTION_DICTS[0]), 
                              isURLExternal(OPTION_DICTS[0]), 
                              faviconURL);
    const iFrame = createIFrame("selectframe", iFramesContainer);
    btn.classList.add("dict-btn-select");
    dictTabButtons.set(btn, iFrame);

    selectList.setAttribute("id", "dict-select");
    selectButtonBox.setAttribute("id", "select-btn-box");
    selectButtonBox.appendChild(selectList); // add select AFTER button
    dictTabsLayoutContainer.appendChild(selectButtonBox);
  
    OPTION_DICTS.forEach((dict) => {
      const option = document.createElement("option");
      const origIndex = TERM_DICTS.indexOf(dict);
      const domain = getDictURLDomain(dict);
      option.textContent = domain;
      option.setAttribute("value", origIndex);
      //option.dataset.dictId = origIndex;
      option.dataset.dictExternal = isURLExternal(dict);
      option.dataset.tabOpened = 1 - isURLExternal(dict);
      selectList.appendChild(option);
    });

    selectList.addEventListener("change", (e) => {
      const optionVal = e.target.value;
      const optionEl = e.target.selectedOptions[0];
      const domain = getDictURLDomain(TERM_DICTS[optionVal]);
      const btnLabel = domain.split("www.").splice(-1)[0];
      const faviconURL = getFavicon(domain);
      const faviconEl = document.createElement("img"); // img elements get deleted after "change" event. so we create them after each change
      faviconEl.src = faviconURL;
      
      btn.dataset.dictId = optionVal;
      btn.dataset.dictExternal = optionEl.dataset.dictExternal;
      btn.textContent = btnLabel;
      btn.dataset.tabOpened = optionEl.dataset.tabOpened;
      btn.prepend(faviconEl);
      
      //faviconEl.classList("dict-btn-img");
      if (optionEl.dataset.dictExternal == 1) {
        loadDictPage(optionVal, "");

        const arrowEl = document.createElement("img");
        arrowEl.src = "../static/icn/arrow-out.svg";
        arrowEl.classList.add("dict-btn-external-img");
        btn.appendChild(arrowEl);
      } else {
        loadDictPage(optionVal, iFrame);
        activateTab(btn, dictTabButtons);
      }
    });
  }
  
  // create image button
  const imageBtn = createTabBtn("", dictTabsContainer, -1, 0);
  imageBtn.setAttribute("id", "dict-image-btn");
  imageBtn.setAttribute("title", "Look up images for the term");
  const imageFrame = createIFrame("imageframe", iFramesContainer);

  dictTabButtons.set(imageBtn, imageFrame);
  
  // set first frame as active (for final: need to save active tab and retrieve it)
  const [firstBtn, firstFrame] = dictTabButtons.entries().next().value;
  firstBtn.classList.add("dict-btn-active");
  firstBtn.dataset.tabOpened = 1;
  firstFrame.classList.add("dict-active");

  dictTabsContainer.addEventListener("click", (e) => {
    const clickedTab = e.target.closest(".dict-btn");
    if (!clickedTab) return;

    const dictID = clickedTab.dataset.dictId;
    // const clickedTab = e.target; 
    const isExternal = clickedTab.dataset.dictExternal;
    let iFrame = dictTabButtons.get(clickedTab);
    if (isExternal == 1) iFrame = "";
    if (clickedTab.dataset.tabOpened == 0) {
      //const dictID = clickedTab.dataset.dictId;
      loadDictPage(dictID, iFrame);
    }
    // checking for iFrame is effectively equal to checking for external
    if (iFrame) {
      activateTab(clickedTab, dictTabButtons);
      if (isExternal == 0) {
        clickedTab.dataset.tabOpened = 1;
      }
    }
  });

  window.addEventListener("message", function(event) {
    if (event.data.event === "LuteTermFormOpened") {
      dictTabButtons.forEach((iframe, btn) => {
        btn.dataset.tabOpened = 0;
      });

      const activeTab = document.querySelector(".dict-btn-active");
      const iFrame = dictTabButtons.get(activeTab);
      const dictID = activeTab.dataset.dictId;
      loadDictPage(dictID, iFrame);

      dictContainer.style.display = "flex";
      dictContainer.style.flexDirection = "column";
    }
  });
}

function activateTab(tab, allTabs) {
  const iFrame = allTabs.get(tab);
  allTabs.forEach((iframe, btn) => {
    btn.classList.remove("dict-btn-active");
    if (iframe) iframe.classList.remove("dict-active");
  });
  
  tab.classList.add("dict-btn-active");
  if (iFrame) iFrame.classList.add("dict-active");
}

function loadDictPage(dictID, iFrame) {
  //const iFrameName = iFrame.getAttribute("name") ? iFrame : "";
  const term = wordFrame.contentDocument.getElementById("text").value;

  if (dictID == -1) {
    do_image_lookup(term, iFrame);
  } else {
    const dict = TERM_DICTS[dictID];
    //const is_external = (activeTab.dataset.dictExternal == 1) ? true : false;
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
    btn.dataset.dictExternal = external;
    if (external == 1) {
      const arrowEl = document.createElement("img");
      arrowEl.src = "../static/icn/arrow-out.svg";
      arrowEl.classList.add("dict-btn-external-img");
      btn.appendChild(arrowEl);
    }
  }

  btn.classList.add("dict-btn");

  if (faviconURL) {
    const faviconEl = document.createElement("img");
    //faviconEl.classList("dict-btn-img");
    faviconEl.src = faviconURL;
    btn.prepend(faviconEl);
  }
  
  parent.appendChild(btn);

  return btn;
}

function isURLExternal(dictURL) {
  return (dictURL.charAt(0) == '*') ? 1 : 0; 
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

  // const is_bing = (dicturl.indexOf('www.bing.com') != -1);
  // if (is_bing) {
  //   let use_text = text;
  //   const binghash = dicturl.replace('https://www.bing.com/images/search?', '');
  //   const url = `/bing/search/${langid}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
  //   document.querySelector(`[name="${iframe}"]`).setAttribute("src", url);
  //   return;
  // }

  if (iframe) {
    // console.log(iframe);
    loadIFrameDictionary(dicturl, text, iframe);
  } else {
    // TODO zzfuture fix: fix_language_dict_asterisk
    // The URL shouldn not be prepended with trash
    // (e.g. "*http://" means "open an external window", while
    // "http://" means "this can be opened in an iframe."
    // Instead, each dict should have an "is_external" property.
    dicturl = dicturl.slice(1);
    const url = get_lookup_url(dicturl, text);
    
    return open_new_lookup_window(url);
  }
}

function loadIFrameDictionary(dicturl, text, iframe) {
  const url = get_lookup_url(dicturl, text);
  iframe.setAttribute("src", url);
}

const open_new_lookup_window = function(url) {
  window.open(
    url,
    'otherwin',
    'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no'
  );
};

const get_lookup_url = function(dicturl, term) {
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
};


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

// function getDictTabSetting() {
//   getFromLocalStorage("dictTabsCount", 0);
// }

// function saveDictTabSetting() {
//   const el = document.querySelector("#language + #submit");
//   el.addEventListener("click", () => {
//     const dictTabsCountVal = document.getElementById("dict_tabs").value;
//     localStorage.setItem("dictTabsCount", dictTabsCountVal);
//   });
  
// }

createDictTabs();