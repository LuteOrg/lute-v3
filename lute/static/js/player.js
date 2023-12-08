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
  if (lastPlayTime) timeline.value = lastPlayTime;

  playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
  changeVolume();
  resetPlaybackRate();
  // changeTimelinePosition();
};

// function activateBookmark(pos) {
//   const activeBookmarkMarker = document.createElement("div");
//   marker.classList.add("active-marker");
//   timelineContainer.appendChild(marker);
//   activeBookmarkMarker.style.cssText = `
//                         left: ${pos}%;
//                         width: 0;
//                         height: 0;
//                         border-left: 5px solid transparent;
//                         border-right: 5px solid transparent;
//                         border-top: 7px solid #555;
//                         position: absolute;
//                         top: -7px;
//                         transform: translate(-50%);`;
// }

function addMarker(pos) {
  const marker = document.createElement("div");
  marker.classList.add(`marker-${pos}`);
  timelineContainer.appendChild(marker);
  marker.style.cssText = `
                          position: absolute;
                          left: ${pos}%;
                          height: 1rem;
                          top: 0;
                          width: 1%;
                          transform: translate(-50%, 0);
                          background-color: orangered;
                          box-sizing: border-box;
                          user-select: none;
                          pointer-events: none;
                          `;
}

// function getAudioName() {
//   let audioPath = document.getElementById("#audio_file").value;
//   console.log(audioPath);
//   if (audioPath) {
//     let startIndex =
//       audioPath.indexOf("\\") >= 0
//         ? audioPath.lastIndexOf("\\")
//         : audioPath.lastIndexOf("/");
//     let filename = audioPath.substring(startIndex);
//     if (filename.indexOf("\\") === 0 || filename.indexOf("/") === 0) {
//       filename = filename.substring(1);
//     }
//   }
// }

// browseButton.addEventListener("input", function () {
//   const audioFile = document.getElementById("#audio_file").files[0];
//   player.src = URL.createObjectURL(audioFile);
// });

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
  if (player.duration) {
    player.currentTime = (timeline.value / 100) * player.duration;
  }
}

function changeTimelinePosition() {
  // const timelinePosition = (player.currentTime / player.duration) * 100;
  timelinePositionPercent = convertTimeToPercentage();
  timeline.style.backgroundSize = `${timelinePositionPercent}% 100%`;
  timeline.value = timelinePositionPercent;
  currentTimeElement.textContent = calculateTime(player.currentTime);

  lastPlayTime = Number(Number(timeline.value).toPrecision(3));
  console.log(lastPlayTime);
}

function convertTimeToPercentage() {
  return (player.currentTime / player.duration) * 100;
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
  if (player.duration){
    if (player.paused) {
      player.play();
      // playBtn.style.backgroundImage = 'url("/static/icn/pause.svg")';
    } else {
      player.pause();
      // playBtn.style.backgroundImage = 'url("/static/icn/play.svg")';
    }
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

bookmarkSaveBtn.addEventListener("click", function () {
  const markerPos = Number(convertTimeToPercentage().toPrecision(3));

  if (bookmarksArray.includes(markerPos)) return;

  addMarker(markerPos);
  // activateBookmark(markerPos);
  // activeBookmark = markerPos;
  bookmarksArray.push(markerPos);
  bookmarksArray.sort(function (a, b) {
    return a - b;
  });

  console.log(bookmarksArray);
});

bookmarkDeleteBtn.addEventListener("click", function() {
  if (lastPlayTime) {
    console.log(lastPlayTime);

    const markerDiv = document.querySelector(`.marker-${lastPlayTime}`);
    if (markerDiv) {
      markerDiv.remove();
      const ind = bookmarksArray.indexOf(lastPlayTime);
      bookmarksArray.splice(ind, 1);
    }

    console.log(bookmarksArray);
  }
})

// function jumpToBookmark(oper) {
//   if (activeBookmark) {
//     let ind;

//     if (oper === "prev") ind = bookmarksArray.indexOf(activeBookmark) - 1;
//     else ind = bookmarksArray.indexOf(activeBookmark) + 1;

//     const m = bookmarksArray[ind];
//     activeBookmark = m;
//     timeline.value = m;
//     updateCurrentTime();
//     // console.log(m);
//     // console.log(calculateTime(player.currentTime));
//   }
// }

bookmarkPrevBtn.addEventListener("click", function () {
  jumpToBookmark("prev");
});
bookmarkNextBtn.addEventListener("click", function () {
  jumpToBookmark("next");
});

function jumpToBookmark(oper) {
  if (lastPlayTime) {
    let ind;

    // console.log(`lastPlayTime initially is ${lastPlayTime}`);
    
    if (oper === "next") ind = bookmarksArray.findIndex((element) => element > lastPlayTime);
    else ind = bookmarksArray.findLastIndex((element) => element < lastPlayTime);
    // console.log(`matchedInd is ${bookmarksArray[matchedInd]}`)
    if (ind == -1) return;
    // else ind = ind;

    const m = bookmarksArray[ind];
    // activeBookmark = m;
    timeline.value = m;
    lastPlayTime = m;
    updateCurrentTime();
    // console.log(`m is ${m}`);
    // console.log(`lastPlayTime after is ${lastPlayTime}`);
    // console.log(calculateTime(player.currentTime));
  }
}
