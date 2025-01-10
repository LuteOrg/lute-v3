"""
All customizable user hotkeys.
"""

import pprint
import yaml


# Hotkeys and descriptions.
_ALL_HOTKEY_DATA = """
Copy:
- hotkey: hotkey_CopySentence
  desc: Copy the sentence of the current word
- hotkey: hotkey_CopyPara
  desc: Copy the paragraph of the current word
- hotkey: hotkey_CopyPage
  desc: Copy the full page

Misc:
- hotkey: hotkey_Bookmark
  desc: Bookmark the current page
- hotkey: hotkey_EditPage
  desc: Edit the current page
- hotkey: hotkey_NextTheme
  desc: Change to the next theme
- hotkey: hotkey_ToggleHighlight
  desc: Toggle highlights
- hotkey: hotkey_ToggleFocus
  desc: Toggle focus mode
- hotkey: hotkey_SaveTerm
  desc: Save term in term form

Navigation:
- hotkey: hotkey_StartHover
  desc: Deselect all words
- hotkey: hotkey_PrevWord
  desc: Move to previous word
- hotkey: hotkey_NextWord
  desc: Move to next word
- hotkey: hotkey_PrevUnknownWord
  desc: Move to previous unknown word
- hotkey: hotkey_NextUnknownWord
  desc: Move to next unknown word
- hotkey: hotkey_PrevSentence
  desc: Move to previous sentence
- hotkey: hotkey_NextSentence
  desc: Move to next sentence

Paging:
- hotkey: hotkey_PreviousPage
  desc: Go to previous page, do not mark current page read
- hotkey: hotkey_NextPage
  desc: Go to next page, do not mark current page read
- hotkey: hotkey_MarkReadWellKnown
  desc: Set remaining unknown words to Well Known, mark page as read, go to next page
- hotkey: hotkey_MarkRead
  desc: Mark page as read, go to next page
- hotkey: hotkey_MarkReadWellKnown
  desc: Set remaining unknown words to Well Known, mark page as read, go to next page

Translate:
- hotkey: hotkey_TranslateSentence
  desc: Translate the sentence of the current word
- hotkey: hotkey_TranslatePara
  desc: Translate the paragraph of the current word
- hotkey: hotkey_TranslatePage
  desc: Translate the full page

Update status:
- hotkey: hotkey_Status1
  desc: Set status to 1
- hotkey: hotkey_Status2
  desc: Set status to 2
- hotkey: hotkey_Status3
  desc: Set status to 3
- hotkey: hotkey_Status4
  desc: Set status to 4
- hotkey: hotkey_Status5
  desc: Set status to 5
- hotkey: hotkey_StatusIgnore
  desc: Set status to Ignore
- hotkey: hotkey_StatusWellKnown
  desc: Set status to Well Known
- hotkey: hotkey_StatusUp
  desc: Bump the status up by 1
- hotkey: hotkey_StatusDown
  desc: Bump that status down by 1
- hotkey: hotkey_DeleteTerm
  desc: Delete term (set status to Unknown)
"""


# Initial hotkey values
#
# Only *some* of the hotkeys have default values assigned, as these
# hotkeys were initially set in the early releases of Lute.
#
# Any new hotkeys added *MUST NOT* have defaults assigned, as users
# may have already setup their hotkeys, and we can't assume that a
# given key combination is free:
_initial_values = {
    "hotkey_StartHover": "Escape",
    "hotkey_PrevWord": "ArrowLeft",
    "hotkey_NextWord": "ArrowRight",
    "hotkey_Status1": "Digit1",
    "hotkey_Status2": "Digit2",
    "hotkey_Status3": "Digit3",
    "hotkey_Status4": "Digit4",
    "hotkey_Status5": "Digit5",
    "hotkey_StatusIgnore": "KeyI",
    "hotkey_StatusWellKnown": "KeyW",
    "hotkey_StatusUp": "ArrowUp",
    "hotkey_StatusDown": "ArrowDown",
    "hotkey_TranslateSentence": "KeyT",
    "hotkey_TranslatePara": "shift+KeyT",
    "hotkey_CopySentence": "KeyC",
    "hotkey_CopyPara": "shift+KeyC",
    "hotkey_Bookmark": "KeyB",
    "hotkey_NextTheme": "KeyM",
    "hotkey_ToggleHighlight": "KeyH",
    "hotkey_ToggleFocus": "KeyF",
    "hotkey_SaveTerm": "ctrl+Enter",
}


def initial_hotkey_defaults():
    """
    Get initial hotkeys and defaults (or empty string).
    Used for db initialization.
    """
    y = yaml.safe_load(_ALL_HOTKEY_DATA)
    hks = []
    for _, keys in y.items():
        hks.extend([k["hotkey"] for k in keys])
    ret = {h: _initial_values.get(h, "") for h in hks}
    return ret


def categorized_hotkeys():
    "Hotkeys by category.  Used by routes."
    y = yaml.safe_load(_ALL_HOTKEY_DATA)
    ordered_keys = [
        "Navigation",
        "Update status",
        "Paging",
        "Translate",
        "Copy",
        "Misc",
    ]
    if set(ordered_keys) != set(y.keys()):
        raise RuntimeError("ordered_keys doesn't match expected")
    ret = {k: [h["hotkey"] for h in y[k]] for k in ordered_keys}
    return ret


def hotkey_descriptions():
    """
    Get hotkeys and descriptions.  Used by routes.
    """
    y = yaml.safe_load(_ALL_HOTKEY_DATA)
    return {key["hotkey"]: key["desc"] for group in y.values() for key in group}


if __name__ == "__main__":
    print("---")
    pprint.pprint(categorized_hotkeys())
    print("---")
    pprint.pprint(initial_hotkey_defaults())
    print("---")
    pprint.pprint(hotkey_descriptions())
