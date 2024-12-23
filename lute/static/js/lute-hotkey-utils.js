/**
 * Get the pressed keys as a string, eg 'meta-KeyC', 'shift-KeyA'.
 *
 * If only meta/alt/ctl/shift are pressed, returns something like 'meta-MetaLeft'.
 */
function get_pressed_keys_as_string(event) {
  const keys = [];

  // Check for modifier keys
  if (event.ctrlKey) keys.push('ctrl');
  if (event.shiftKey) keys.push('shift');
  if (event.altKey) keys.push('alt');
  if (event.metaKey) keys.push('meta');

  keys.push(event.code);
  const ret = keys.join('+');
  // console.log(`got hotkey = ${ret}`);
  return ret;
}


/**
 * Function for legacy get_pressed_keys_as_string
 *
 * Per https://github.com/LuteOrg/lute-v3/issues/541, Lute used to use
 * the event.key for keyboard shortcuts, but that caused problems for
 * changing keyboard layouts.
 *
 * This function uses the old way of "event.key" to find the key
 * pressed, as a fallback for users who have the old keyboard
 * mappings.
 */
function _legacy_pressed_key_string(event) {
  const keys = [];

  // Check for modifier keys
  if (event.ctrlKey) keys.push('ctrl');
  if (event.shiftKey) keys.push('shift');
  if (event.altKey) keys.push('alt');
  if (event.metaKey) keys.push('meta');

  // Map special keys to names if needed
  const keyMap = {
    ' ': 'space'
  };

  if (event.key == null) {
    // window.alert("no key for event?");
    return null;
  }

  const actual_key = keyMap[event.key] || event.key.toLowerCase();
  if (['shift', 'ctrl', 'alt', 'meta', 'control'].includes(actual_key))
    return null

  keys.push(actual_key);
  const ret = keys.join('+');
  // console.log(`got hotkey = ${ret}`);
  return ret;
}


/**
 * get the "hotkey name" (e.g. "hotkey_Status5") for the given event
 * from LUTE_USER_HOTKEYS.
 *
 * First try to get the name using the pressed key string, then use
 * the legacy event.
 *
 * Returns null if no match found.
 */
function get_hotkey_name(event) {
  let s = get_pressed_keys_as_string(event);
  if (s in LUTE_USER_HOTKEYS)
    return LUTE_USER_HOTKEYS[s];
  s = _legacy_pressed_key_string(event);
  if (s in LUTE_USER_HOTKEYS)
    return LUTE_USER_HOTKEYS[s];
  return null;
}
