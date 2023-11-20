CLI commands.

Note the lute.app_factory has to be specified as the `--app`.

Samples:

```
flask --app lute.app_factory cli --help

flask --app lute.app_factory cli language_export English ./hello.csv
```

See the  help for a command:

```
flask --app lute.app_factory cli language_export --help

Usage: flask cli language_export [OPTIONS] LANGUAGE OUTPUT_PATH

  Get all terms from active books in the language, and write a data file of
  term frequencies and children.
```