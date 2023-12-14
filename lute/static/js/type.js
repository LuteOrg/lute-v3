"use strict";

const typeControlContainer = document.querySelector("#type-control-container");
const typeButton = document.querySelector("#text-control-btn");
const typePlusButton = document.querySelector(".type-plus");
const typeMinusButton = document.querySelector(".type-minus");
const fontField = document.querySelector(".type-control-size input");
// const textItems = document.querySelectorAll("span.textitem");

const lhPlusButton = document.querySelector(".lh-plus");
const lhMinusButton = document.querySelector(".lh-minus");
const lhField = document.querySelector(".type-control-lh input");

// console.log(`items are ${textItems[0]}`);

typeButton.addEventListener("click", ()=> {
  const textItem = document.querySelector("span.textitem");
  // console.log(getFontSize(textItem));
  fontField.value = `${getFontSize(textItem)}px`;
  lhField.value = `${getLineHeight(textItem)}`;
})


// // typeButton.addEventListener("click", (e)=> {
// //   e.stopPropagation();
// // }, true)
// typeButton.addEventListener("click", (e)=> {
//   e.stopPropagation();
//   typeControlContainer.classList.toggle("hide-type");
//   // e.preventDefault();
// })


// function closeOnOutsideClick(element) {
//   document.addEventListener("click", (e) => {
//     if (!element.contains(e.target)) {
//       console.log(element);
//       if (!element.classList.contains("hide-type")) {
//         element.classList.add("hide-type");

//       }
//     }
//   })
// }

// closeOnOutsideClick(typeControlContainer);

// typeControlContainer.addEventListener("focusout", (e) => {
//   e.target.classList.add("hide-type");
// })

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

fontField.addEventListener("change", (e) => {
  const textItems = document.querySelectorAll("span.textitem");
  const size = `${parseFloat(e.target.value)}px`;
  console.log(size);

  textItems.forEach((item) => {
    setFontSize(item, size);
  })
})

function getLineHeight(element) {
  const elementComputedStyle = window.getComputedStyle(element);
  console.log((parseFloat(elementComputedStyle.marginBottom) * 2 + getFontSize(element)) / getFontSize(element));
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
  
  const textItems = document.querySelectorAll("span.textitem");
  const currentSize = getLineHeight(textItems[0]);

  const add = (operation === "+");
  const newSize = add ? currentSize + 0.1 : currentSize - 0.1;

  console.log(newSize, newSize.toPrecision(2));
  textItems.forEach((item) => {
    setLineHeight(item, Number(newSize.toPrecision(2)));
  })
}

function resizeFont(operation) {
  // console.log("click +");
  const textItems = document.querySelectorAll("span.textitem");
  const currentSize = getFontSize(textItems[0]);
  // console.log(`${parseFloat(currentSize) + 1} + px`);
  const add = (operation === "+");
  const newSize = add ? `${currentSize + 1}px` : `${currentSize - 1}px`;
  textItems.forEach((item) => {
    setFontSize(item, newSize);
  })
}