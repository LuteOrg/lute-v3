# `lute3-thai`

A Thai parser for Lute (`lute3`) using the `pythainlp` library.

## Installation

See the [Lute manual](https://luteorg.github.io/lute-manual/install/plugins.html).

## Usage

When this parser is installed, you can add "Thai" as a
language to Lute, which comes with a simple story.

## Notes

Thai is tough to parse!  In particular, it is sometimes hard to know where sentences are split.

Some sentence splitting characters are specified in the Thai language
definition, which you can edit.

**This parser also assumes that spaces are used as sentence delimiters**.

In many cases, this is a reasonable assumption (e.g. see the stories
at [Thai
Reader](https://seasite.niu.edu/thai/thaireader/frameset.htm)), but in
sometimes this can be incorrect.  For example, numbers and English
words are often written with spaces surrounding them, as in this
single sentence from a news story:

ออกคำสั่งในวันเสาร์ที่ 2 พ.ย. 2567 ให้ทหาร 5,000 นาย กับ ตำรวจและเจ้าหน้าที่กองกำลังป้องกันพลเรือนอีก 5,000 นาย ไปเสริมกำลังเจ้าหน้าที่ในแคว้นบาเลนเซีย .

Hopefully in the future some smart codes will be able to improve the parsing to handle such situations ... but for now, Lute can give you some support for reading in Thai.