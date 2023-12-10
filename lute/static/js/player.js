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

// const markerOverlay = document.querySelector(".marker");
const timelineContainer = document.querySelector("#timeline-container");
const bookmarkSaveBtn = document.querySelector("#bkm-save-btn");
const bookmarkDeleteBtn = document.querySelector("#bkm-delete-btn");
const bookmarkPrevBtn = document.querySelector("#bkm-prev-btn");
const bookmarkNextBtn = document.querySelector("#bkm-next-btn");

const theTextItems = document.querySelectorAll("#thetext .textitem");

var bookmarksArray = [];
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
  for (b of bookmarksArray) {
    add_bookmark_marker(b);
  }
  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
  changeVolume();
  resetPlaybackRate();
};

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
  console.log(`time %, t = ${t}, max = ${timeline.max}`);
  return (t * 100 / timeline.max);
}

playBtn.addEventListener("click", function () {
  if ((player.duration ?? 0) == 0)
    return;
  if (player.paused)
    player.play();
  else
    player.pause();
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
 * Ajax post player data updates every 2 seconds.
 */

var last_sent_pos = null;

function post_player_data() {
  const bookid = $('#book_id').val();
  const bookmarks = $('#book_audio_bookmarks').val();
  var currentPosition = player.currentTime;
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

let _post_if_changed = function() {
  var currentPosition = player.currentTime;
  if (last_sent_pos == currentPosition) {
    // console.log("Same pos, skipping");
    return;
  }
  post_player_data();
};

// Post every 2 seconds, good enough.
setInterval(_post_if_changed(), 2000);


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
 * Bookmark management.
 */

let add_bookmark_marker = function(currtime) {
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

let _update_bookmarks_control = function() {
  bs = bookmarksArray.map(b => `${b}`).join(';');
  $('#book_audio_bookmarks').val(bs);
};

function marker_classname_from_time(timeline_value) {
  return `marker-${timeline_value}`.replace('.', '-');
}

bookmarkSaveBtn.addEventListener("click", function () {
  // Note that for the time, we use the timeline.value, which has
  // step=0.1 and so is quantized to 0.1 of a second.  Should be good
  // enough.
  const t = timeline.value;
  add_bookmark(t);
  _update_bookmarks_control();
  post_player_data();
  // console.log(`added ${t} to bookmarksArray ${bookmarksArray}`);
});


function add_bookmark(t) {
  if (bookmarksArray.includes(t))
    return;
  add_bookmark_marker(t);
  bookmarksArray.push(t);
  bookmarksArray.sort(function (a, b) {
    return a - b;
  });
}


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
  if (ind == -1) {
    // Not found.
    return;
  }
  
  bookmarksArray.splice(ind, 1);
  _update_bookmarks_control();
  post_player_data();
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
