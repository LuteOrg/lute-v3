const readPaneLeft = document.querySelector("#read_pane_left")
const player = document.querySelector("#player");
const timeline = document.querySelector(".timeline");
const volumeLine = document.querySelector(".volume");
const playBtn = document.querySelector("#play-btn");
const playBtnIcon = document.querySelector("#play-btn span");
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

const playerContainer = document.querySelector(".audio-player-container");
const bookmarkContainer = document.querySelector(".bookmark-markers-container");
const timelineContainer = document.querySelector("#timeline-container");
const bookmarkSaveDeleteBtn = document.querySelector("#bkm-save-btn");
const bookmarkPrevBtn = document.querySelector("#bkm-prev-btn");
const bookmarkNextBtn = document.querySelector("#bkm-next-btn");

var bookmarksArray = [];
let lastPlayTime = null;
let playerSticky = localStorage.getItem("player-sticky") ?? 0;
if (playerSticky != 0) readPaneLeft.classList.add("sticky-player");

let jumpTimeBy = Number(rewindAmountOption.value);

player.onloadedmetadata = function () {
  durationElement.textContent = timeToDisplayString(player.duration);
  timeline.max = player.duration;
  for (b of bookmarksArray) {
    addBookmarkMarker(b);
  }
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
  const seconds = (secs % 60).toFixed(1);
  const m = minutes < 10 ? `0${minutes}` : `${minutes}`;
  const s = (secs % 60) < 10 ? `0${seconds}` : `${seconds}`;
  return `${m}:${s}`;
}

function updateCurrentTime() {
  if ((player.duration ?? 0) == 0)
    return;
  player.currentTime = timeline.value;
  // console.log(`currTime = ${player.currentTime}`);
}

function timeToPercent(t) {
  // console.log(`time %, t = ${t}, max = ${timeline.max}`);
  return (t * 100 / timeline.max);
}

playBtn.addEventListener("click", function () {
  if ((player.duration ?? 0) == 0 || isNaN(player.duration))
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

player.addEventListener("timeupdate", function () {
  // const timelinePosition = (player.currentTime / player.duration) * 100;
  timeline.value = player.currentTime;

  const t = timeline.value;  // quantized value.
  timeline.style.backgroundSize = `${timeToPercent(t)}% 100%`;
  currentTimeElement.textContent = timeToDisplayString(timeline.value);
  lastPlayTime = timeline.value;

  if (bookmarksArray.includes(Number(timeline.value))) toggleBookmarkIcon("on");
  else toggleBookmarkIcon("off");
});

timeline.addEventListener("input", updateCurrentTime);


/* ****************************
 * Ajax post player data updates every 2 seconds.
 */

var last_sent_pos = null;

function post_player_data() {
  const bookid = $('#book_id').val();
  const bookmarks = $('#book_audio_bookmarks').val();
  var currentPosition = player.currentTime;
  // console.log(`posting curr pos = ${currentPosition}`);
  data = {
    bookid: bookid,
    position: currentPosition,
    bookmarks: bookmarks,
  };
  $.ajax({
    url: '/read/save_player_data',
    method: 'POST',
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8"
  }).done(function(d) {
    last_sent_pos = currentPosition;
  });
}

let post_if_changed = function() {
  // console.log(`called post_if_changed, with currTime = ${player.currentTime}`);
  var currentPosition = player.currentTime;
  if (last_sent_pos == currentPosition) {
    // console.log("Same pos, skipping");
    return;
  }
  post_player_data();
};

// Post every 2 seconds, good enough.
function start_player_post_loop() {
  setInterval(post_if_changed, 2000);
}

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
  // add the class to readpaneleft and not the player itself 
  // so that we can get it's sibling (paneright) to add a bottom margin in css
  readPaneLeft.classList.toggle("sticky-player");
  // save sticky state to local storage
  localStorage.setItem("player-sticky", 1 - Number(playerSticky))
  // remove focus off the button so it doesn't accidentally get activated by spacebar
  pin.blur();
});


/* ****************************
 * Bookmark management.
 */

let addBookmarkMarker = function(currtime) {
  // console.log(`adding bookmark for currtime = ${currtime}`);
  const marker = document.createElement("div");
  marker.classList.add(marker_classname_from_time(currtime));
  bookmarkContainer.appendChild(marker);
  marker.style.cssText =
    `position: absolute;
     left: ${timeToPercent(currtime)}%;
     height: calc(var(--timeline-height) + 1px);
     top: 0;
     width: min(5px, 1%);
     transform: translate(-50%, 0);
     background-color: var(--audio-color-2);
     box-sizing: border-box;
     border-radius: 1px;
     user-select: none;
     pointer-events: none;`;
}

let _update_bookmarks_control = function() {
  bs = bookmarksArray.map(b => `${b}`).join(';');
  $('#book_audio_bookmarks').val(bs);
};

function marker_classname_from_time(timeline_value) {
  return `marker-${timeline_value}`.replace('.', '-');
}

bookmarkSaveDeleteBtn.addEventListener("click", function () {
  // Note that for the time, we use the timeline.value, which has
  // step=0.1 and so is quantized to 0.1 of a second.  Should be good
  // enough.
  const t = Number(timeline.value);

  if (bookmarksArray.includes(t)) deleteBookmark(t);
  else addBookmark(t);

  _update_bookmarks_control();
  post_player_data();
  // console.log(`added ${t} to bookmarksArray ${bookmarksArray}`);
});


function addBookmark(t) {
  if (bookmarksArray.includes(t))
    return;
  addBookmarkMarker(t);
  bookmarksArray.push(t);
  bookmarksArray.sort(function (a, b) {
    return a - b;
  });

  toggleBookmarkIcon("on");
}


function deleteBookmark(t) {
  // const t = timeline.value;
  if (t == null) {
    // console.log('null timeline value.');
    return;
  }
  // console.log(`pre-delete, have ${bookmarksArray}, t = ${t}`);
  const fixedBa = bookmarksArray.map((e) => e.toFixed(1));
  const findt = Number(t).toFixed(1);
  // console.log(`t = ${t}, type = ${typeof(t)}, findt = ${findt}`);
  const ind = fixedBa.indexOf(`${findt}`);
  if (ind == -1) {
    // console.log(`time ${t} not found.`);
    return;
  }

  const mc = marker_classname_from_time(t);
  // console.log(`with tval ${t}, deleting class ${mc}`);
  const markerDiv = document.querySelector(`.${mc}`);
  if (markerDiv) {
    markerDiv.remove();
  }

  bookmarksArray.splice(ind, 1);

  toggleBookmarkIcon("off");
  // _update_bookmarks_control();
  // post_player_data();
  // console.log(`post-delete, have ${bookmarksArray}`);
}

function toggleBookmarkIcon(state) {
  let url = 'url("/static/icn/bookmark-on.svg")';
  if (state == "off") url = 'url("/static/icn/bookmark-off.svg")';

  bookmarkSaveDeleteBtn.style.backgroundImage = url;
}


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
    lastPlayTime = 0;
  // console.log(`jumpToBookmark from time ${lastPlayTime}, currently have ${bookmarksArray}`);

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
  post_player_data();
}


/* ****************************
 * Keyboard shortcuts
 */

window.addEventListener("keydown", function (e) {
  // console.log(e.code);
  if (e.code == "Space") {
    // prevent scrolling when space is pressed
    // and it seems this fixes the issue where there's flashing
    // where one keydown event continiously makes the button play and pause
    e.preventDefault()
    togglePlayPause();
    // if (e.target == document.body) {
    //   // prevent scrolling when space is pressed
    //   e.preventDefault()
    // };
  }
});