Lute language definitions.

This directory of languages is added as a git submodule to lute itself.

# Adding a language

For each new language:

1. create a directory with the name of the language (really it can be anything)
2. create `definition.yaml` from `_templates/definition.yaml.example`, fill it in.  The file name **matters**.
3. create a story .txt file from `_templates/story.yaml.example`, fill it in.  The file name **does not matter**.

## Verifying

To verify the files, run

```
python verify_files.py
```

This does a simple sanity check of the files, it's not an exhaustive check.

# Notes

## Why is this a git submodule?

This directory/repo is just data, so ideally it would be pulled in at build time, but I had problems including the data files when packaging with flit.  Submodules was the easiest solution I could come up with at the time.  There is probably an easier way to do it, but this way works fine.

To include the latest language data in the lute build, update the submodule ref as needed ... docs to come.