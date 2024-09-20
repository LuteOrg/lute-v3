"use strict";

/* NOTE: this code uses some globals from resize.js */
// TODO refactor: remove js global state!

const domObserver = new MutationObserver((mutationList, observer) => {
  incrementFontSize(0);
  incrementLineHeight(0);
  setColumnCount(null);
});

domObserver.observe(theText, {childList: true, subtree: true});

// Helper function to add event listeners
function addClickHandler(selector, callback, value) {
  const button = document.querySelector(selector);
  button.addEventListener("click", () => callback(value));
}

// Add button handlers.
addClickHandler(".font-plus", incrementFontSize, 1);
addClickHandler(".font-minus", incrementFontSize, -1);
addClickHandler(".lh-plus", incrementLineHeight, 0.1);
addClickHandler(".lh-minus", incrementLineHeight, -0.1);
addClickHandler(".width-plus", setTextWidth, 1.05);
addClickHandler(".width-minus", setTextWidth, 0.95);
addClickHandler(".column-one", setColumnCount, 1);
addClickHandler(".column-two", setColumnCount, 2);


function incrementFontSize(delta) {
  const textItems = document.querySelectorAll("span.textitem");
  const s = window.getComputedStyle(textItems[0]);
  const fontDefault = parseFloat(s.fontSize);
  const STORAGE_KEY = "fontSize";
  const fontSize = getFromLocalStorage(STORAGE_KEY, fontDefault);

  const newSize = clamp(fontSize + delta, 1, 50);

  const sizeRem = `${convertPixelsToRem(newSize)}rem`;
  textItems.forEach((item) => {
    item.style.fontSize = sizeRem;
  });

  localStorage.setItem(STORAGE_KEY, newSize);
}

function convertPixelsToRem(sizePx) {
  const bodyFontSize =  window.getComputedStyle(document.querySelector("body")).fontSize;
  const sizeRem = sizePx / parseFloat(bodyFontSize);
  return sizeRem;
}

function incrementLineHeight(delta) {
  const paras = document.querySelectorAll("#thetext p");
  const s = window.getComputedStyle(paras[0]);
  const lhDefault = parseFloat(s.getPropertyValue('line-height'));

  const STORAGE_KEY = "paraLineHeight";
  let current_h = getFromLocalStorage(STORAGE_KEY, lhDefault);
  current_h = Number(current_h.toPrecision(2));
  let new_h = clamp(current_h + delta, 1.3, 5);

  paras.forEach((p) => { p.style.lineHeight = new_h; });
  localStorage.setItem(STORAGE_KEY, new_h);
}

function setTextWidth(factor) {
  const STORAGE_KEY = "textWidth";
  const currentWidth = getFromLocalStorage(STORAGE_KEY, widthDefault);
  const newWidth = clamp(currentWidth * factor, 25, 95);

  readPaneLeft.style.width = `${newWidth}%`;
  readPaneRight.style.width = `${(100 - newWidth) * getReadPaneWidthRatio()}%`;

  localStorage.setItem(STORAGE_KEY, newWidth);
}

function setColumnCount(num) {
  let columnCount = num;
  if (columnCount == null) {
    const s = window.getComputedStyle(theText);
    columnCount = getFromLocalStorage("columnCount", s.columnCount);
  }
  theText.style.columnCount = columnCount;
  localStorage.setItem("columnCount", columnCount);
}
