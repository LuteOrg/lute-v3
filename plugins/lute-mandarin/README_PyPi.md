# `lute3-mandarin`

A Mandarin parser for Lute (`lute3`) using the `jieba` library, and
`pypinyin` for readings.

## Installation

See the [Lute manual](https://luteorg.github.io/lute-manual/install/plugins.html).

## Usage

When this parser is installed, you can add "Mandarin Chinese" as a
language to Lute, which comes with a simple story.

## Parsing exceptions

Sometimes `jieba` groups too many characters together when parsing.
For example, it returns "清华大学" as a single word of four
characters, which might not be correct.

You can specify how Lute should correct these cases by adding some
simple "rules" to the file
`plugins/lute_mandarin/parser_exceptions.txt` found in your Lute
`data` directory.  This file is automatically created when Lute
starts.  Each rule contains the characters of the word as parsed by
`jieba`, with regular commas added where the word should be split.

Some examples:

| File content | Results when parsing "清华大学" |
| --- | --- |
| (empty file) | "清华大学" |
| <pre><code>清华,大学</code></pre> | Two tokens, "清华" and "大学" (the single token is split in two) |
| <pre><code>清,华,大,学</code></pre> | Four tokens, "清", "华", "大", "学" |
| <pre><code>清华,大学<br>大,学</code></pre> | Three tokens, "清华", "大, "学" (results are recursively broken down if rules are found) |
