const player = document.querySelector("#player");
const timeline = document.querySelector(".timeline");
const volumeLine = document.querySelector(".volume");
const playBtn = document.querySelector("#play-btn");
const playBtnIcon = document.querySelector("#play-btn span");
const browseButton = document.querySelector("#audio_file");
const durationContainer = document.querySelector(".duration-container");
const durationElement = document.querySelector(".duration-container .duration");
const currentTimeElement = document.querySelector(
  ".duration-container .current-time"
);
const rewindButton = document.querySelector("#rewind-btn");
const ffButton = document.querySelector("#ff-btn");
const playbackRateButton = document.querySelector("#playback-rate-btn");
const playbackRateIndicator = document.querySelector("#playback-rate-btn span");
const rewindAmountOption = document.querySelector("#rewind-option");

// const markerOverlay = document.querySelector(".marker");
const timelineContainer = document.querySelector("#timeline-container");
const bookmarkSaveBtn = document.querySelector("#bkm-save-btn");
const bookmarkDeleteBtn = document.querySelector("#bkm-delete-btn");
const bookmarkPrevBtn = document.querySelector("#bkm-prev-btn");
const bookmarkNextBtn = document.querySelector("#bkm-next-btn");

const theTextItems = document.querySelectorAll("#thetext .textitem");

const bookmarksArray = [];
let lastPlayTime = null;

let jumpTimeBy = Number(rewindAmountOption.value);

player.onloadedmetadata = function () {
  durationElement.textContent = timeToDisplayString(player.duration);
  timeline.max = player.duration;
  if (lastPlayTime) timeline.value = lastPlayTime;

  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
  changeVolume();
  resetPlaybackRate();
};


function marker_classname_from_time(timeline_value) {
  return `marker-${timeline_value}`.replace('.', '-');
}

function addBookmark(currtime) {
  // console.log(`adding bookmark for currtime = ${currtime}`);
  const marker = document.createElement("div");
  marker.classList.add(marker_classname_from_time(currtime));
  timelineContainer.appendChild(marker);
  marker.style.cssText =
    `position: absolute;
     left: ${timeToPercent(currtime)}%;
     height: 1.1rem;
     top: 0;
     width: 1%;
     transform: translate(-50%, 0);
     background-color: orangered;
     box-sizing: border-box;
     user-select: none;
     pointer-events: none;`;
}

function jumpToBookmark(oper) {
  if (lastPlayTime == null)
    return;
  // console.log(`jumping to bookmark from time ${lastPlayTime}, currently have ${bookmarksArray}`);

  // Note for the findIndex, we have to use Number(d), as it
  // appears that javascript can sometimes do string comparisons.
  // e.g., if I had bookmarks [ 93.4, 224, 600 ], jumping backwards
  // from 224 doesn't find 93.4, because "93.4" > "224".
  if (oper === "next") {
    ind = bookmarksArray.findIndex((d) => Number(d) > lastPlayTime);
  }
  else {
    ind = bookmarksArray.findLastIndex((d) => Number(d) < lastPlayTime);
  }
  if (ind == -1) {
    // console.log('not found');
    return;
  }

  const m = bookmarksArray[ind];
  // console.log(`ind is ${ind} => bookmarksArray entry ${m}`);
  timeline.value = m;
  lastPlayTime = m;
  updateCurrentTime();
}

function timeToDisplayString(secs) {
  const minutes = Math.floor(secs / 60);
  const seconds = parseFloat((secs % 60).toFixed(1));
  const returnedSeconds = seconds < 10 ? `0${seconds}` : `${seconds}`;
  return `${minutes}:${returnedSeconds}`;
}

function disableScroll() {
  scrollTop = document.documentElement.scrollTop;
  scrollLeft = document.documentElement.scrollLeft;

  window.onscroll = function () {
    window.scrollTo(scrollLeft, scrollTop);
  };
}

function enableScroll() {
  window.onscroll = function () {};
}

function resetPlaybackRate() {
  player.playbackRate = 1.0;
  playbackRateIndicator.textContent = "1.0";
}

function changeVolume() {
  player.volume = volumeLine.value / 100;
  volumeLine.style.backgroundSize = `${volumeLine.value}% 100%`;
}

function updateCurrentTime() {
  if ((player.duration ?? 0) == 0)
    return;

  player.currentTime = timeline.value;
}

function changeTimelinePosition() {
  // const timelinePosition = (player.currentTime / player.duration) * 100;
  timeline.value = player.currentTime;

  const t = timeline.value;  // quantized value.
  timeline.style.backgroundSize = `${timeToPercent(t)}% 100%`;
  currentTimeElement.textContent = timeToDisplayString(timeline.value);
  lastPlayTime = timeline.value;
}

function timeToPercent(t) {
  return (t * 100 / player.duration);
}

rewindAmountOption.addEventListener("change", function () {
  jumpTimeBy = Number(rewindAmountOption.value);
});

browseButton.addEventListener("change", function (e) {
  if (e.target.files[0]) {
    // player.setAttribute("src", `/static/${e.target.files[0].name}`);
    // const audioFile = document.getElementById("#audio_file").files[0];
    player.src = URL.createObjectURL(e.target.files[0]);
  }
});

playBtn.addEventListener("click", function () {
  if ((player.duration ?? 0) == 0)
    return;

  if (player.paused) {
    player.play();
  }
  else {
    player.pause();
  }
});

player.addEventListener("pause", function () {
  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
});

player.addEventListener("play", function () {
  playBtn.style.backgroundImage = 'url("/static/icn/pause.svg")';
});

ffButton.addEventListener("click", function () {
  player.currentTime = player.currentTime + jumpTimeBy;
});

rewindButton.addEventListener("click", function () {
  player.currentTime = player.currentTime - jumpTimeBy;
});

playbackRateButton.addEventListener("wheel", function (e) {
  if (e.deltaY < 0)
    player.playbackRate += 0.1;
  else
    player.playbackRate -= 0.1;

  playbackRateIndicator.textContent = player.playbackRate.toFixed(1);
});

theTextItems.forEach((item) =>
  item.addEventListener("mousedown", () => player.pause())
);

playbackRateButton.addEventListener("mouseover", disableScroll);
playbackRateButton.addEventListener("mouseleave", enableScroll);
playbackRateButton.addEventListener("click", resetPlaybackRate);
player.addEventListener("timeupdate", changeTimelinePosition);
timeline.addEventListener("input", updateCurrentTime);
volumeLine.addEventListener("input", changeVolume);

bookmarkPrevBtn.addEventListener("click", function () {
  jumpToBookmark("prev");
});

bookmarkNextBtn.addEventListener("click", function () {
  jumpToBookmark("next");
});

bookmarkSaveBtn.addEventListener("click", function () {
  // Note that for the time, we use the timeline.value, which has
  // step=0.1 and so is quantized to 0.1 of a second.  Should be good
  // enough.
  const t = timeline.value;
  if (bookmarksArray.includes(t))
    return;

  addBookmark(t);
  bookmarksArray.push(t);
  bookmarksArray.sort(function (a, b) {
    return a - b;
  });
  // console.log(`added ${t} to bookmarksArray ${bookmarksArray}`);
});

bookmarkDeleteBtn.addEventListener("click", function() {
  const t = timeline.value;
  if (t == null)
    return;

  mc = marker_classname_from_time(t);
  // console.log(`with tval ${t}, deleting class ${mc}`);
  const markerDiv = document.querySelector(`.${mc}`);
  if (markerDiv) {
    markerDiv.remove();
  }

  // console.log(`pre-delete, have ${bookmarksArray}`);
  const ind = bookmarksArray.indexOf(t);
  if (ind != -1)
    bookmarksArray.splice(ind, 1);
  // console.log(`post-delete, have ${bookmarksArray}`);
})
