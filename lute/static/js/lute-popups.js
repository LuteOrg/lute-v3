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
      topWin.lute_popup_window = topWin.open(url, 'dictwin', settings);
    }
  }

  /* Close all popups. */
  function close_all_popups() {
    const topWin = window.top;
    if (topWin.lute_popup_window && !topWin.lute_popup_window.closed) {
      topWin.lute_popup_window.close();
    }
  }

  // Exported functions.
  return {
    open_popup: open_popup,
    close_all_popups: close_all_popups
  };
})();
