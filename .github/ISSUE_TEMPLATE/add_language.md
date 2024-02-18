---
name: Add a language
about: Fill in a form with data to request adding a new language to Lute's demos
title: 'Add language: [name]'
labels: 'enhancement'
assignees: ''

---

**NOTE: this form is for you to share your language settings with other new users.  If you're a GitHub user, it would be super if you could instead create a Pull Request with your language settings, using the files in this repo's `lute/db/demo/language` and `/stories` as references.  Thanks!**

If your language settings are working well for you, please share them with other new users by providing the following data:

* name: <language-name>
* show_romanization: <true or false>
* right_to_left: <true or false>
* parser_type: spacedel or mecab   (probably "spacedel" is the correct one, "space delimited")
* split_sentences: characters to split sentences on, if the defaults aren't good
* split_sentence_exceptions:
* word_chars:
* character_substitutions:  (if there are any special characters)

Dictionaries.  A list of one or more entries:

* use_for: terms or sentences
* type: embedded or popup
* url

It's good to have a short demonstration story available as well.  Please paste a family-friendly (!) story below:

```
Title: [story-title]
Source: [url source or similar]

[content here]
```