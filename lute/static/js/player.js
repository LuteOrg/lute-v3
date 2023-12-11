const readPaneLeft = document.querySelector("#read_pane_left")
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
const skipbackButton = document.querySelector("#skip-back-btn");
const playbackRateButton = document.querySelector("#playback-rate-btn");
const playbackRateIndicator = document.querySelector("#playback-rate-btn span");
const rewindAmountOption = document.querySelector("#rewind-option");

const pinButton = document.querySelector("#pin");

// const markerOverlay = document.querySelector(".marker");
const playerContainer = document.querySelector(".audio-player-container");
const timelineContainer = document.querySelector("#timeline-container");
const bookmarkSaveBtn = document.querySelector("#bkm-save-btn");
const bookmarkDeleteBtn = document.querySelector("#bkm-delete-btn");
const bookmarkPrevBtn = document.querySelector("#bkm-prev-btn");
const bookmarkNextBtn = document.querySelector("#bkm-next-btn");

const theTextItems = document.querySelectorAll("#thetext .textitem");

const bookmarksArray = [];
let lastPlayTime = null;

let jumpTimeBy = Number(rewindAmountOption.value);

browseButton.addEventListener("change", function (e) {
  if (e.target.files[0]) {
    player.src = URL.createObjectURL(e.target.files[0]);
  }
});

player.onloadedmetadata = function () {
  durationElement.textContent = timeToDisplayString(player.duration);
  timeline.max = player.duration;
  if (lastPlayTime) timeline.value = lastPlayTime;

  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
  changeVolume();
  resetPlaybackRate();
};

function togglePlayPause() {
  if (player.paused)
    player.play();
  else
    player.pause();
}

function timeToDisplayString(secs) {
  const minutes = Math.floor(secs / 60);
  const seconds = parseFloat((secs % 60).toFixed(1));
  const m = minutes < 10 ? `0${minutes}` : `${minutes}`;
  const s = seconds < 10 ? `0${seconds}` : `${seconds}`;
  return `${m}:${s}`;
}

function updateCurrentTime() {
  if ((player.duration ?? 0) == 0)
    return;
  player.currentTime = timeline.value;
}

function timeToPercent(t) {
  return (t * 100 / player.duration);
}

playBtn.addEventListener("click", function () {
  if ((player.duration ?? 0) == 0)
    return;
  togglePlayPause()
});

player.addEventListener("pause", function () {
  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
});

// Listening for form opened event created by lute/templates/term/_form.html.
window.addEventListener("message", function(event) {
    if (event.data.event === "LuteTermFormOpened") {
        player.pause();
    }
});

player.addEventListener("play", function () {
  playBtn.style.backgroundImage = 'url("/static/icn/pause.svg")';
});

theTextItems.forEach((item) =>
  item.addEventListener("mousedown", () => player.pause())
);

player.addEventListener("timeupdate", function () {
  // const timelinePosition = (player.currentTime / player.duration) * 100;
  timeline.value = player.currentTime;

  const t = timeline.value;  // quantized value.
  timeline.style.backgroundSize = `${timeToPercent(t)}% 100%`;
  currentTimeElement.textContent = timeToDisplayString(timeline.value);
  lastPlayTime = timeline.value;
});

timeline.addEventListener("input", updateCurrentTime);


/* ****************************
 * Volume.
 */

function changeVolume() {
  player.volume = volumeLine.value / 100;
  volumeLine.style.backgroundSize = `${volumeLine.value}% 100%`;
}

volumeLine.addEventListener("input", changeVolume);


/* ****************************
 * Rewind, ff.
 */

rewindAmountOption.addEventListener("change", function () {
  jumpTimeBy = Number(rewindAmountOption.value);
});

ffButton.addEventListener("click", function () {
  player.currentTime = player.currentTime + jumpTimeBy;
});

rewindButton.addEventListener("click", function () {
  player.currentTime = player.currentTime - jumpTimeBy;
});

skipbackButton.addEventListener("click", function () {
  player.currentTime = 0;
});

/* ****************************
 * Playback rate.
 */

playbackRateButton.addEventListener("mouseover", function() {
  scrollLeft = document.documentElement.scrollLeft;
  scrollTop = document.documentElement.scrollTop;
  window.onscroll = function () {
    window.scrollTo(scrollLeft, scrollTop);
  };
});

playbackRateButton.addEventListener("mouseleave", function() {
  window.onscroll = function () {};
});

playbackRateButton.addEventListener("wheel", function (e) {
  let r = player.playbackRate;
  if (e.deltaY < 0)
    r += 0.1;
  else
    r -= 0.1;
  if (r < 0.1)
    r = 0.1;
  if (r > 10)
    r = 10;
  player.playbackRate = r
  playbackRateIndicator.textContent = player.playbackRate.toFixed(1);
});

playbackRateButton.addEventListener("click", resetPlaybackRate);

function resetPlaybackRate() {
  player.playbackRate = 1.0;
  playbackRateIndicator.textContent = "1.0";
}

/* ****************************
 * Toggle player sticky.
 */

pin.addEventListener("click", function() {
  readPaneLeft.classList.toggle("sticky-player");
})

/* ****************************
 * Bookmark management.
 */

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

function marker_classname_from_time(timeline_value) {
  return `marker-${timeline_value}`.replace('.', '-');
}

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


/* ****************************
 * Bookmark navigation.
 */

bookmarkPrevBtn.addEventListener("click", function () {
  jumpToBookmark("prev");
});

bookmarkNextBtn.addEventListener("click", function () {
  jumpToBookmark("next");
});

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


/* ****************************
 * Keyboard shortcuts
 */

document.addEventListener("keydown", function (e) {
  if (e.code == "Space") {
    togglePlayPause();
  }
})

// prevent scrolling when space is pressed
window.addEventListener('keydown', function(e) {
  if(e.code == "Space" && e.target == document.body) {
    e.preventDefault();
  }
});
