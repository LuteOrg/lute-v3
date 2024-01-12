"use strict";

let textItems;
let fontDefault;
let lhDefault;
let columnDefault;

const fontPlusButton = document.querySelector(".font-plus");
const fontMinusButton = document.querySelector(".font-minus");

const lhPlusButton = document.querySelector(".lh-plus");
const lhMinusButton = document.querySelector(".lh-minus");

const widthPlusButton = document.querySelector(".width-plus");
const widthMinusButton = document.querySelector(".width-minus");

const oneColButton = document.querySelector(".column-one");
const twoColButton = document.querySelector(".column-two");

// const theText = document.querySelector("#thetext");

const domObserver = new MutationObserver((mutationList, observer) => {
  textItems = document.querySelectorAll("span.textitem");

  fontDefault = getFontSize(textItems[0]);
  lhDefault = getLineHeight(textItems[0]);
  columnDefault = getColumnCount();

  const fontSize = getFromLocalStorage("fontSize", fontDefault);
  const lhSize = getFromLocalStorage("lineHeight", lhDefault);
  const columnCount = getFromLocalStorage("columnCount", columnDefault);

  textItems.forEach((item) => {
    setFontSize(item, `${convertPixelsToRem(fontSize)}rem`);
    setLineHeight(item, Number(lhSize.toPrecision(2)));
  });

  theText.style.columnCount = columnCount;
});

domObserver.observe(theText, {childList: true, subtree: true});

fontPlusButton.addEventListener("click", () => {
  resizeFont("+");
});

fontMinusButton.addEventListener("click", () => {
  resizeFont("-");
});

lhPlusButton.addEventListener("click", () => {
  resizeLineHeight("+");
});

lhMinusButton.addEventListener("click", () => {
  resizeLineHeight("-");
});

widthPlusButton.addEventListener("click", () => {
  changeTextWidth("+");
});

widthMinusButton.addEventListener("click", () => {
  changeTextWidth("-");
});

oneColButton.addEventListener("click", () => {
  changeColumnCount(1);
});

twoColButton.addEventListener("click", () => {
  changeColumnCount(2);
});

function changeColumnCount(num) {
  theText.style.columnCount = num;
  localStorage.setItem("columnCount", num);
}

function getFontSize(element) {
  const elementComputedStyle = window.getComputedStyle(element);
  return parseFloat(elementComputedStyle.fontSize);
}

function getLineHeight(element) {
  const elementComputedStyle = window.getComputedStyle(element);
  return Number(((parseFloat(elementComputedStyle.marginBottom) * 2 + getFontSize(element)) / getFontSize(element)).toPrecision(2));
  // return parseFloat(elementComputedStyle.marginBottom);
}

function getColumnCount() {
  const elementComputedStyle = window.getComputedStyle(theText);
  return elementComputedStyle.columnCount;
}

function setFontSize(element, size) {
  element.style.fontSize = size;
}

function setLineHeight(element, size) {
  const marginVal = (getFontSize(element) * size - getFontSize(element)) * 0.5;
  element.style.marginBottom = `${marginVal}px`;
}

function resizeLineHeight(operation) {
  const currentSize = getFromLocalStorage("lineHeight", lhDefault);
  const add = (operation === "+");
  let newSize = add ? currentSize + 0.1 : currentSize - 0.1;
  newSize = clamp(newSize, 1, 5);

  textItems.forEach((item) => {
    setLineHeight(item, Number(newSize.toPrecision(2)));
  });

  localStorage.setItem("lineHeight", newSize.toPrecision(2));
}

function resizeFont(operation) {
  const currentSize = getFromLocalStorage("fontSize", fontDefault);
  const add = (operation === "+");
  let newSize = add ? currentSize + 1 : currentSize - 1;
  newSize = clamp(newSize, 1, 50);

  textItems.forEach((item) => {
    setFontSize(item, `${convertPixelsToRem(newSize)}rem`);
  });

  localStorage.setItem("fontSize", newSize);
}

function changeTextWidth(operation) {
  const currentWidth = getFromLocalStorage("textWidth", widthDefault);
  const add = (operation === "+");

  let newWidth = add ? currentWidth + currentWidth * 0.05 : currentWidth - currentWidth * 0.05;

  newWidth = clamp(newWidth, 25, 95);

  readPaneLeft.style.width = `${newWidth}%`;
  readPaneRight.style.width = `${(100 - newWidth) * getReadPaneWidthRatio()}%`;

  localStorage.setItem("textWidth", newWidth);
}

function convertPixelsToRem(sizePx) {
  const bodyFontSize =  window.getComputedStyle(document.querySelector("body")).fontSize;
  const sizeRem = sizePx / parseFloat(bodyFontSize);
  return sizeRem;
}