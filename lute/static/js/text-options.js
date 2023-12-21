"use strict";

let textItems;
let fontDefault;
let lhDefault;
let widthDefault;
let columnDefault;

const fontPlusButton = document.querySelector(".font-plus");
const fontMinusButton = document.querySelector(".font-minus");

const lhPlusButton = document.querySelector(".lh-plus");
const lhMinusButton = document.querySelector(".lh-minus");

const widthPlusButton = document.querySelector(".width-plus");
const widthMinusButton = document.querySelector(".width-minus");

const oneColButton = document.querySelector(".column-one");
const twoColButton = document.querySelector(".column-two");

const theText = document.querySelector("#thetext");
const readPaneRight = document.querySelector("#read_pane_right");
// const readPaneLeft = document.querySelector("#read_pane_left");

const domObserver = new MutationObserver((mutationList, observer) => {
  textItems = document.querySelectorAll("span.textitem");

  fontDefault = getFontSize(textItems[0]);
  lhDefault = getLineHeight(textItems[0]);
  widthDefault = getTextWidthPercentage();
  columnDefault = getColumnCount();

  const fontSize = getFromLocalStorage("fontSize", fontDefault);
  const lhSize = getFromLocalStorage("lineHeight", lhDefault);
  const width = getFromLocalStorage("textWidth", widthDefault);
  const columnCount = getFromLocalStorage("columnCount", columnDefault);

  textItems.forEach((item) => {
    setFontSize(item, `${convertPixelsToRem(fontSize)}rem`);
    setLineHeight(item, Number(lhSize.toPrecision(2)));
  });

  readPaneLeft.style.width = `${width}%`;
  readPaneRight.style.width = `${(100 - width) * getReadPaneWidthRatio()}%`;
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

function getTextWidthPercentage() {
  // returns percentage value
  const elementComputedStyle = window.getComputedStyle(readPaneLeft);
  return (parseFloat(elementComputedStyle.getPropertyValue("width")) / parseFloat(window.getComputedStyle(readPaneContainer).getPropertyValue("width"))) * 100;
  // return parseFloat(elementComputedStyle.width);
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
  console.log(newSize);
  newSize = clamp(newSize, 1, 50);
  console.log(newSize);

  textItems.forEach((item) => {
    setFontSize(item, `${convertPixelsToRem(newSize)}rem`);
  });

  localStorage.setItem("fontSize", newSize);
}

function changeTextWidth(operation) {
  const currentWidth = getFromLocalStorage("textWidth", widthDefault);
  const add = (operation === "+");

  let newWidth = add ? currentWidth + currentWidth * 0.05 : currentWidth - currentWidth * 0.05;

  newWidth = clamp(newWidth, 25, 75);

  readPaneLeft.style.width = `${newWidth}%`;
  readPaneRight.style.width = `${(100 - newWidth) * getReadPaneWidthRatio()}%`;

  localStorage.setItem("textWidth", newWidth);
}

function convertPixelsToRem(sizePx) {
  const bodyFontSize =  window.getComputedStyle(document.querySelector("body")).fontSize;
  const sizeRem = sizePx / parseFloat(bodyFontSize);
  return sizeRem;
}

function getFromLocalStorage(item, defaultVal) {
  // return Number(localStorage.getItem(item) ?? defaultVal);
  const storageVal = localStorage.getItem(item);
  
  if ((!storageVal) || isNaN(storageVal)) {
    return Number(defaultVal);
  } else {
    return Number(storageVal);
  }
}

function clamp (num, min, max) {
  return Math.min(Math.max(num, min), max);
}

// because right side is fixed. it's width value is different. need to find ratio
// basically: when gridContainer width is 100%, this doesn't mean that it takes the whole 
// viewport width. it can be less than that. but for the right side it's an absolute percentage value
function getReadPaneWidthRatio() {
  return parseFloat(window.getComputedStyle(readPaneContainer).getPropertyValue("width")) / parseFloat(document.documentElement.clientWidth);
}
