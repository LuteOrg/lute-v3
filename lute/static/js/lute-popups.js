/* Lute popups. */

const LutePopups = (function() {

  /* Open a new popup, or reuse existing. */
  function open_popup(url, settings) {
    const topWin = window.top;

    if (topWin.lute_popup_window && !topWin.lute_popup_window.closed) {
      topWin.lute_popup_window.location = url;
      topWin.lute_popup_window.focus();
    }
    else {
      const pop = topWin.open(url, 'dictwin', settings);
      topWin.lute_popup_window = pop;
      if (!topWin.lute_popup_windows) {
        topWin.lute_popup_windows = [];
      }
      topWin.lute_popup_windows.push(pop);
    }
  }

  /* Close all popups. */
  function close_all_popups() {
    if (window.top.lute_popup_windows) {
      window.top.lute_popup_windows.forEach(function(w) {
        if (w && !w.closed) {
          w.close();
        }
      });
    }
    if (window.top.lute_popup_window && !window.top.lute_popup_window.closed) {
      window.top.lute_popup_window.close();
    }
  }

  // Exported functions.
  return {
    open_popup: open_popup,
    close_all_popups: close_all_popups
  };
})();
