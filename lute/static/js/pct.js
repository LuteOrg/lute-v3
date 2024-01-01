"use strict";

// const bookTable = document.getElementById("booktable");
// const domObserver = new MutationObserver((mutationList, observer) => {
//   showFractionStats();
// });

// domObserver.observe(bookTable, {childList: true, subtree: true});

const wbtn = document.getElementById("wcnt");

wbtn.addEventListener("click", showFractionStats);

function  showFractionStats() {
  for (const book in statusPct) {
    for (const status in statusPct[book]){
      const icon = document.querySelector(`.status-pct${status}-${book}`);
      const iconSpan = icon.children[0];
      const iconPct = statusPct[book][status];
      icon.style.flex = `${iconPct}`;
      if (iconPct > 0.1) iconSpan.textContent = `\xa0${(iconPct * 100).toFixed(0)}%`;
    }
  }

  const pctConts = document.querySelectorAll(".status-pct-icon-container");
  pctConts.forEach((pctCont) => pctCont.classList.add("show-pct"));
}