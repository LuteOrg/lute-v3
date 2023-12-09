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
// let activeBookmark = null;

//let duration = 0;
let jumpTimeBy = Number(rewindAmountOption.value);

player.onloadedmetadata = function () {
  //console.log(player.duration);
  durationElement.textContent = calculateTime(player.duration);
  // durationContainer.style.display = "flex";
  //player.playbackRate = 1.0;
  // console.log(lastPlayTime);
  // if (lastPlayTime) player.currentTime = lastPlayTime;
  timeline.max = player.duration;
  if (lastPlayTime) timeline.value = lastPlayTime;

  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
  changeVolume();
  resetPlaybackRate();
  // changeTimelinePosition();
};


function marker_classname_from_time(timeline_value) {
  return `marker-${timeline_value}`.replace('.', '-');
}

function addBookmark(currtime) {
  console.log(`adding bookmark for currtime = ${currtime}`);
  const marker = document.createElement("div");
  marker.classList.add(marker_classname_from_time(currtime));
  timelineContainer.appendChild(marker);

  pos_percent = Math.floor((currtime * 100) / player.duration);
  marker.style.cssText = `
                          position: absolute;
                          left: ${pos_percent}%;
                          height: 1.1rem;
                          top: 0;
                          width: 1%;
                          transform: translate(-50%, 0);
                          background-color: orangered;
                          box-sizing: border-box;
                          user-select: none;
                          pointer-events: none;
                          `;
}

function jumpToBookmark(oper) {
  if (lastPlayTime == null)
    return;

  console.log(`jumping to bookmark from time ${lastPlayTime}, currently have ${bookmarksArray}`);

  // Note for the findIndex, we have to use Number(element), as it
  // appears that javascript can sometimes do string comparisons.
  // e.g., if I had bookmarks [ 93.4, 224, 600 ], jumping backwards
  // from 224 doesn't find 93.4, because "93.4" > "224".
  if (oper === "next") {
    ind = bookmarksArray.findIndex((element) => Number(element) > lastPlayTime);
  }
  else {
    ind = bookmarksArray.findLastIndex((element) => Number(element) < lastPlayTime);
  }

  if (ind == -1) {
    console.log('not found');
    return;
  }

  const m = bookmarksArray[ind];
  console.log(`ind is ${ind} => bookmarksArray entry ${m}`);

  // activeBookmark = m;
  timeline.value = m;
  lastPlayTime = m;
  console.log(`timeline.value = ${timeline.value}`);
  console.log(`lastPlayTime = ${lastPlayTime}`);

  // call to updateCurrentTime() is required to fix the timeline and
  // update the UI.  This also quantizes the lastPlayTime to 0.1s
  // precision.
  updateCurrentTime();

  // console.log(`m is ${m}`);
  // console.log(`lastPlayTime after is ${lastPlayTime}`);
  // console.log(calculateTime(player.currentTime));
}

function calculateTime(secs) {
  const minutes = Math.floor(secs / 60);
  const seconds = Math.floor(secs % 60);
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
  // console.log(player.duration);
  if ((player.duration ?? 0) == 0)
    return;

  player.currentTime = timeline.value;
}

function changeTimelinePosition() {
  // const timelinePosition = (player.currentTime / player.duration) * 100;
  timelinePositionPercent = convertTimeToPercentage();
  timeline.style.backgroundSize = `${timelinePositionPercent}% 100%`;
  timeline.value = player.currentTime;
  console.log(`timeline value = ${timeline.value}`);
  currentTimeElement.textContent = calculateTime(player.currentTime);

  lastPlayTime = timeline.value;
  console.log(`lastPlayTime = ${lastPlayTime}`);
}

function convertTimeToPercentage() {
  console.log(`curr time: ${player.currentTime}`);
  console.log(`duration: ${player.duration}`);
  const pct = (player.currentTime / player.duration) * 100;
  console.log(`percent: ${pct}`);
  return pct;
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
    // playBtn.style.backgroundImage = 'url("/static/icn/pause.svg")';
  } else {
    player.pause();
    // playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
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
  if (e.deltaY < 0) player.playbackRate += 0.1;
  else player.playbackRate -= 0.1;

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
  const currtime = timeline.value;

  if (bookmarksArray.includes(currtime))
    return;

  addBookmark(currtime);
  // activateBookmark(markerPos);
  // activeBookmark = markerPos;
  bookmarksArray.push(currtime);
  bookmarksArray.sort(function (a, b) {
    return a - b;
  });

  console.log(`added ${currtime} to bookmarksArray ${bookmarksArray}`);
});

bookmarkDeleteBtn.addEventListener("click", function() {
  if (lastPlayTime == null)
    return;

  t = marker_classname_from_time(timeline.value);
  console.log(`pre-delete, have ${bookmarksArray}`);
  console.log(`with tval ${timeline.value}, deleting class ${t}`);
  const markerDiv = document.querySelector(`.${t}`);
  if (markerDiv) {
    markerDiv.remove();
    const ind = bookmarksArray.indexOf(lastPlayTime);
    bookmarksArray.splice(ind, 1);
  }
  console.log(`post-delete, have ${bookmarksArray}`);
})
