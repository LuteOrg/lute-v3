/**
 * Get the pressed keys as a string, eg 'meta-c', 'shift-a'.
 *
 * Note that there _must_ be a "regular" key pressed as well.
 * If only meta/alt/ctl/shift are pressed, returns null.
 */
function get_pressed_keys_as_string(event) {
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
