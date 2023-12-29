"use strict";

let mouse_pos;
let widthDefault;
let trHeightDefault;
const borderWidth = 4;
const wordFrame = document.getElementById("wordframeid");
const dictFrame = document.getElementById("dictframeid");
const dictFrameCont = document.querySelector(".dictframecontainer");
const readPaneRight = document.querySelector("#read_pane_right");

applyInitialPaneSizes();

function resizeCol(e){
  const dx = mouse_pos - e.x;
  mouse_pos = e.x;
  // getting the width with computedStyle doesn't seem to be working correctly.
  // getting width directly, but for this initial width must be set via javascript 
  // so the style is inline for this code to work
  const currentWidthLeft = readPaneLeft.style.width;
  const readPaneWidth = parseFloat(window.getComputedStyle(readPaneContainer).getPropertyValue("width"));
  // const currentWidthLeft = parseFloat(window.getComputedStyle(readPaneLeft).getPropertyValue("width"));

  let lfWidthPct = parseFloat(currentWidthLeft) - (dx / readPaneWidth * 100);
  lfWidthPct = clamp(lfWidthPct, 25, 95);
  const rtWidthPct = (100 - lfWidthPct) * getReadPaneWidthRatio();

  readPaneLeft.style.width = `${lfWidthPct}%`;
  readPaneRight.style.width = `${rtWidthPct}%`;

  localStorage.setItem("textWidth", lfWidthPct);
}

function resizeRow(e){
  const dx = mouse_pos - e.y;
  mouse_pos = e.y;
  // const currentWidth = getFromLocalStorage("textWidth", widthDefault);
  const currentHeightWordFrame = parseFloat(window.getComputedStyle(readPaneRight).gridTemplateRows.split(" ")[0]);
  const readPaneRightHeight = parseFloat(window.getComputedStyle(readPaneRight).getPropertyValue("height"));
  // const currentHeightWordFrame = parseFloat(window.getComputedStyle(dictFrameCont).getPropertyValue("height"));
  // const currentHeightWordFrame = parseFloat(dictFrameCont.style.height);
  // console.log(currentHeightWordFrame);
  let wordFrameHeight = (currentHeightWordFrame / readPaneRightHeight * 100) - (dx / readPaneRightHeight * 100);
  wordFrameHeight = clamp(wordFrameHeight, 5, 95);
  // const currentWidthRight = window.getComputedStyle(readPaneRight).width;
  // console.log(currentHeightWord);

  readPaneRight.style.gridTemplateRows = `${wordFrameHeight}% 1fr`;
  // console.log(`${parseInt(currentWidthRight) - dx}px`);
  // readPaneRight.style.width = `${parseInt(currentWidthRight) + dx}px`;
  localStorage.setItem("trHeight", wordFrameHeight);
}

readPaneRight.addEventListener("mousedown", function(e){
  if (e.offsetX < borderWidth) {
    setIFrameStatus("none");
    mouse_pos = e.x;
    document.addEventListener("mousemove", resizeCol);
    e.preventDefault(); // prevent selection
  }
});

// double click -> widen to 95% temporarily (doesn't save state)
readPaneRight.addEventListener("dblclick", function(e){
  if (e.offsetX < borderWidth) {
    // if the width is 95% then return to the last width value
    if (readPaneLeft.style.width == "95%") {
      const width = getFromLocalStorage("textWidth", widthDefault);
      readPaneLeft.style.width = `${width}%`;
      readPaneRight.style.width = `${(100 - width) * getReadPaneWidthRatio()}%`;
    } else {
      readPaneLeft.style.width = "95%";
      readPaneRight.style.width = `${5 * getReadPaneWidthRatio()}%`;
    }
    }
});

dictFrameCont.addEventListener("mousedown", function(e){
  if (e.offsetY < borderWidth) {
    setIFrameStatus("none");
    mouse_pos = e.y;
    document.addEventListener("mousemove", resizeRow);
    e.preventDefault();
  }
});

dictFrameCont.addEventListener("dblclick", function(e){
  if (e.offsetY < borderWidth) {
    if (readPaneRight.style.gridTemplateRows.split(" ")[0] == "5%") {
      readPaneRight.style.gridTemplateRows = `${getFromLocalStorage("trHeight", trHeightDefault)}% 1fr`;
    } else {
      readPaneRight.style.gridTemplateRows = `${5}% 1fr`;
    }
  }
});

document.addEventListener("mouseup", function(){
  document.removeEventListener("mousemove", resizeCol);
  document.removeEventListener("mousemove", resizeRow);
  setIFrameStatus("unset");
});

// hide horizontal line
window.addEventListener("message", function(event) {
  if (event.data.event === "LuteTermFormOpened") {
    dictFrameCont.style.opacity = "1";
  }
});

// if the iframes are clickable mousemove doesn't work correctly
function setIFrameStatus(status) {
  wordFrame.style.pointerEvents = status;
  dictFrame.style.pointerEvents = status;
}

// because right side is fixed. it's width value is different. need to find ratio
// basically: when gridContainer width is 100%, this doesn't mean that it takes the whole 
// viewport width. it can be less than that. but for the right side it's an absolute percentage value
function getReadPaneWidthRatio() {
  return parseFloat(window.getComputedStyle(readPaneContainer).getPropertyValue("width")) / parseFloat(document.documentElement.clientWidth);
}

function clamp (num, min, max) {
  return Math.min(Math.max(num, min), max);
}

function getTextWidthPercentage() {
  // returns percentage value
  const elementComputedStyle = window.getComputedStyle(readPaneLeft);
  return (parseFloat(elementComputedStyle.getPropertyValue("width")) / parseFloat(window.getComputedStyle(readPaneContainer).getPropertyValue("width"))) * 100;
  // return parseFloat(elementComputedStyle.width);
}

function getWordFrameHeightPercentage() {
  // returns percentage value
  // const elementComputedStyle = window.getComputedStyle(dictFrameCont);
  return (parseFloat(window.getComputedStyle(readPaneRight).gridTemplateRows.split(" ")[0]) / parseFloat(window.getComputedStyle(readPaneRight).getPropertyValue("height"))) * 100;
  // return parseFloat(elementComputedStyle.width);
}

function applyInitialPaneSizes() {
  widthDefault = getTextWidthPercentage();
  trHeightDefault = getWordFrameHeightPercentage();

  const width = getFromLocalStorage("textWidth", widthDefault);
  const height = getFromLocalStorage("trHeight", trHeightDefault);

  readPaneLeft.style.width = `${width}%`;
  readPaneRight.style.width = `${(100 - width) * getReadPaneWidthRatio()}%`;
  readPaneRight.style.gridTemplateRows = `${height}% 1fr`;
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