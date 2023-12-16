"use strict";

let textItems;
const typeControlContainer = document.querySelector("#type-control-container");
const typeButton = document.querySelector("#text-control-btn");
const typePlusButton = document.querySelector(".type-plus");
const typeMinusButton = document.querySelector(".type-minus");
const fontField = document.querySelector(".type-control-size input");

const lhPlusButton = document.querySelector(".lh-plus");
const lhMinusButton = document.querySelector(".lh-minus");
const lhField = document.querySelector(".type-control-lh input");

const widthPlusButton = document.querySelector(".width-plus");
const widthMinusButton = document.querySelector(".width-minus");
const widthField = document.querySelector(".type-control-width input");

const oneColButton = document.querySelector(".column-one");
const twoColButton = document.querySelector(".column-two");
const threeColButton = document.querySelector(".column-three");

const readGridContainer = document.querySelector("#read_grid_container");
const theText = document.querySelector("#thetext");

const domObserver = new MutationObserver((mutationList, observer) => {
  textItems = document.querySelectorAll("span.textitem");
  fontField.value = `${getFontSize(textItems[0])}px`;
  lhField.value = `${getLineHeight(textItems[0])}`;
  widthField.value = `${Math.round(convertWidthValueToPercentage())}%`;

  observer.disconnect();
});

function convertWidthValueToPercentage() {
  const [x, y] = getTextWidth(readGridContainer);
  return x / (x + y) * 100;
}

const clamp = (num, min, max) => Math.min(Math.max(num, min), max);

domObserver.observe(theText, {childList: true, subtree: true});

typeButton.addEventListener("click", (e)=> {
  typeControlContainer.classList.toggle("hide-type");
})

// stop propagation so clicking anything inside the popup
// doesn't trigger type button click event
typeControlContainer.addEventListener("click", (e)=> {
  e.stopPropagation();
  // e.preventDefault();
})

// clicking away closes the popup
document.addEventListener("click", (e) => {
  if (!e.target.closest("#text-control-btn")) {
    typeControlContainer.classList.add("hide-type");
  }
})

typePlusButton.addEventListener("click", () => {
  resizeFont("+")
})

typeMinusButton.addEventListener("click", () => {
  resizeFont("-")
})

lhPlusButton.addEventListener("click", () => {
  // console.log("asd");
  resizeLineHeight("+");
})

lhMinusButton.addEventListener("click", () => {
  resizeLineHeight("-");
})

widthPlusButton.addEventListener("click", () => {
  changeTextWidth("+");
})

widthMinusButton.addEventListener("click", () => {
  changeTextWidth("-");
})

oneColButton.addEventListener("click", () => {
  changeColumnCount(1);
})

twoColButton.addEventListener("click", () => {
  changeColumnCount(2);
})

threeColButton.addEventListener("click", () => {
  changeColumnCount(3);
})

function changeColumnCount(num) {
  theText.style.columnCount = num;
}

function getTextWidth() {
  const elementComputedStyle = window.getComputedStyle(readGridContainer)
  const [x, y] = elementComputedStyle.gridTemplateColumns.split(" ");
  // console.log(parseFloat(x), parseFloat(y));
  return [parseFloat(x), parseFloat(y)];
}

function getLineHeight(element) {
  const elementComputedStyle = window.getComputedStyle(element);
  // console.log((parseFloat(elementComputedStyle.marginBottom) * 2 + getFontSize(element)) / getFontSize(element));
  return Number(((parseFloat(elementComputedStyle.marginBottom) * 2 + getFontSize(element)) / getFontSize(element)).toPrecision(2));
  // return parseFloat(elementComputedStyle.marginBottom);
}

function setLineHeight(element, size) {
  // console.log("set");
  const marginVal = (getFontSize(element) * size - getFontSize(element)) * 0.5;
  element.style.marginBottom = `${marginVal}px`;
}

function getFontSize(element) {
  const elementComputedStyle = window.getComputedStyle(element);
  return parseFloat(elementComputedStyle.fontSize);
}

function setFontSize(element, size) {
  // console.log("set");
  element.style.fontSize = size;
}

function resizeLineHeight(operation) {
  // const textItems = document.querySelectorAll("span.textitem");
  const currentSize = getLineHeight(textItems[0]);

  const add = (operation === "+");
  let newSize = add ? currentSize + 0.1 : currentSize - 0.1;
  // newSize = newSize < 1 ? 1 : newSize;

  // if (newSize < 1)
  newSize = clamp(newSize, 1, 5);

  // console.log(newSize, newSize.toPrecision(2));
  textItems.forEach((item) => {
    setLineHeight(item, Number(newSize.toPrecision(2)));
  })

  lhField.value = Number(newSize.toPrecision(2));
}

fontField.addEventListener("change", (e) => {
  const size = `${parseFloat(e.target.value)}px`;

  textItems.forEach((item) => {
    setFontSize(item, size);
  })
})

lhField.addEventListener("change", (e) => {
  const size = parseFloat(e.target.value);

  textItems.forEach((item) => {
    setLineHeight(item, size);
  })
})

function resizeFont(operation) {
  // console.log("click +");
  // const textItems = document.querySelectorAll("span.textitem");
  const currentSize = getFontSize(textItems[0]);
  // console.log(`${parseFloat(currentSize) + 1} + px`);
  const add = (operation === "+");
  const newSize = add ? currentSize + 1 : currentSize - 1;
  textItems.forEach((item) => {
    setFontSize(item, `${convertPixelsToRem(newSize)}rem`);
    // setFontSize(item, `${newSize}px`);
  })

  fontField.value = `${newSize}px`;
}

function changeTextWidth(operation) {
  const [x, y] = getTextWidth();
  const add = (operation === "+");
  const per = convertWidthValueToPercentage();

  let newWidth = add ? per + per * 0.05 : per - per * 0.05;

  newWidth = clamp(newWidth, 25, 75);

  readGridContainer.style.gridTemplateColumns = `${newWidth}fr ${100 - newWidth}fr`;

  widthField.value = `${Math.round(newWidth)}%`;
}

function convertPixelsToRem(sizePx) {
  const bodyFontSize =  window.getComputedStyle(document.querySelector("body")).fontSize;
  const sizeRem = sizePx / parseFloat(bodyFontSize);
  return sizeRem;
}