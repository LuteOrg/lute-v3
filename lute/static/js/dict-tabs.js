"use strict";

function createDictTabs() {
  const dictButtons = new Map();
  //const TERM_DICTS = ALL_DICTS[LANG_ID].term;
  const dictTabsContainer = document.getElementById("dicttabs");
  const iFramesContainer = document.getElementById("dictframes");

  TERM_DICTS.forEach((dict, index) => {
    let btnLabel = `Dictionary ${String(index).padStart(2, "0")}`;
    let external = 0;

    if (dict.charAt(0) == '*') {
      btnLabel = btnLabel.concat("*");
      let external = 1;
    }
    const btn = createTabBtn(btnLabel, dictTabsContainer, index, external);
    const iFrame = createIFrame(`dict${index}`, iFramesContainer);

    dictButtons.set(btn, iFrame);
  });
  
  // create image button
  const imageBtn = createTabBtn("", dictTabsContainer, -1, 0);
  imageBtn.setAttribute("id", "dict-image-btn");
  imageBtn.setAttribute("title", "Look up images for the term");
  const imageFrame = createIFrame("imageframe", iFramesContainer);

  dictButtons.set(imageBtn, imageFrame);
  
  // set first frame as active (for final: need to save active tab and retrieve it)
  const [firstBtn, firstFrame] = dictButtons.entries().next().value;
  firstBtn.classList.add("dict-btn-active");
  firstBtn.dataset.tabOpened = 1;
  firstFrame.classList.add("dict-active");
  //firstFrame.dataset.dictOpened = 1;

  dictTabsContainer.addEventListener("click", (e) => {
    const dictBtnClicked = e.target.closest(".dict-btn");
    if (!dictBtnClicked) return;

    const clickedBtn = e.target; 
    const is_external = clickedBtn.dataset.dictExternal;

    if (clickedBtn.dataset.tabOpened == 0) {
      loadDictPage(clickedBtn, dictButtons);
    }

    if (is_external == 0) {
      dictButtons.forEach((iframe, btn) => {
        btn.classList.remove("dict-btn-active");
        iframe.classList.remove("dict-active");
      });

      clickedBtn.classList.add("dict-btn-active");
      dictButtons.get(clickedBtn).classList.add("dict-active");
      
      clickedBtn.dataset.tabOpened = 1;
    }
  });

  window.addEventListener("message", function(event) {
    if (event.data.event === "LuteTermFormOpened") {
      dictButtons.forEach((iframe, btn) => {
        btn.dataset.tabOpened = 0;
      });

      const activeTab = document.querySelector(".dict-btn-active");
      loadDictPage(activeTab, dictButtons);

      dictContainer.style.display = "block";
    }
  });
}

function loadDictPage(activeTab, tabButtons) {
  const iFrame = tabButtons.get(activeTab);
  const iFrameName = iFrame.getAttribute("name");
  const dictID = activeTab.dataset.dictId;
  const term = wordFrame.contentDocument.getElementById("text").value;

  if (dictID == -1) {
    do_image_lookup(LANG_ID, term, iFrameName);
  } else {
    const dict = TERM_DICTS[dictID];
    const is_external = (activeTab.dataset.dictExternal == 1) ? true : false;
    show_lookup_page(dict, term, iFrameName, LANG_ID, is_external);
  }
}

function createIFrame(name, parent) {
  const iFrame = document.createElement("iframe");
  iFrame.name = name;
  iFrame.src = "about:blank";
  iFrame.classList.add("dictframe");
  //iFrame.dataset.dictOpened = 0;

  parent.appendChild(iFrame);

  return iFrame;
}

function createTabBtn(label, parent, data, external) {
  const btn = document.createElement("button");
  if (label) btn.textContent = label;
  if (data != null) btn.dataset.dictId = data;
  btn.dataset.dictExternal = external;
  btn.classList.add("dict-btn");
  
  parent.appendChild(btn);

  return btn;
}

/**
   * Either open a new window, or show the result in the correct frame.
   */
function show_lookup_page(dicturl, text, iframe, langid, is_external, allow_open_new_web_page = true) {

  const is_bing = (dicturl.indexOf('www.bing.com') != -1);
  if (is_bing) {
    let use_text = text;
    const binghash = dicturl.replace('https://www.bing.com/images/search?', '');
    const url = `/bing/search/${langid}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
    document.querySelector(`[name="${iframe}"]`).setAttribute("src", url);
    return;
  }

  // TODO zzfuture fix: fix_language_dict_asterisk
  // The URL shouldn not be prepended with trash
  // (e.g. "*http://" means "open an external window", while
  // "http://" means "this can be opened in an iframe."
  // Instead, each dict should have an "is_external" property.
  if (is_external) {
    if (!allow_open_new_web_page) {
      console.log('Declining to open external web page.');
      return;
    }
    dicturl = dicturl.slice(1);
    const url = get_lookup_url(dicturl, text);
    
    return open_new_lookup_window(url);
  }

  // Fallback: open in frame.
  //const url = get_lookup_url(dicturl, text);
  //top.frames.dictframe.setAttribute("src", url);
  loadIFrameDictionary(dicturl, text, iframe);
}

function loadIFrameDictionary(dicturl, text, iframe) {
  const url = get_lookup_url(dicturl, text);
  document.querySelector(`[name="${iframe}"]`).setAttribute("src", url);
}

let open_new_lookup_window = function(url) {
  window.open(
    url,
    'otherwin',
    'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no'
  );
};

let get_lookup_url = function(dicturl, term) {
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
  // console.log(ret);
  return ret;
};


function do_image_lookup(langid, text, imageframe) {
  if (langid == null || langid == '' || parseInt(langid) == 0 || text == null || text == '') {
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
  const url = `/bing/search/${langid}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
  document.querySelector(`[name="${imageframe}"]`).setAttribute("src", url);
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

createDictTabs();