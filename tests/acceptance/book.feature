Feature: Books and stats are available

    Background:
        Given a running site
        And demo languages

    Scenario: I can import text.
        Given I visit "/"
        Given a Spanish book "Hola" with content:
            Hola. Tengo un gato.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Tengo/ /un/ /gato/.

    Scenario: I can force page breaks where I want with "---".
        Given I visit "/"
        Given a Spanish book "Hola" with content:
            Hola. Tengo un gato.
            ---
            Tienes un gato.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Tengo/ /un/ /gato/.

    Scenario: I can import a text file.
        Given I visit "/"
        Given a Spanish book "Hola" from file hola.txt
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

    Scenario: Non-utf-8 text files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file non_utf_8.txt
        Then the page contains "non_utf_8.txt is not utf-8 encoding"

    Scenario: I can import a url.
        Given I visit "/"
        Given a Spanish book from url http://localhost:5000/dev_api/fake_story.html
        Then the page title is Reading "Mi perro."
        And the reading pane shows:
            Hola/. /Tengo/ /un/ /perro/.

    Scenario: I can import an epub file.
        Given I visit "/"
        Given a Spanish book "Hola" from file Hola.epub
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

    Scenario: Invalid epub files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file invalid.epub
        Then the page contains "Could not parse invalid.epub"

    Scenario: Empty files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file invalid_empty.epub
        Then the page contains "invalid_empty.epub is empty."

    Scenario: I can import a PDF file.
        Given I visit "/"
        Given a Spanish book "Hola" from file Hola.pdf
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

    Scenario: Invalid PDF files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file invalid.pdf
        Then the page contains "Could not parse invalid.pdf"

    Scenario: I can import a srt file.
        Given I visit "/"
        Given a Spanish book "Hola" from file Hola.srt
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

    Scenario: Invalid srt files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file invalid.srt
        Then the page contains "Could not parse invalid.srt"

    Scenario: I can import a vtt file.
        Given I visit "/"
        Given a Spanish book "Hola" from file Hola.vtt
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

    Scenario: Invalid vtt files are rejected.
        Given I visit "/"
        Given a Spanish book "Hola" from file invalid.vtt
        Then the page contains "Could not parse invalid.vtt"

    Scenario: Books and stats are shown on the first page.
        Given I visit "/"
        Given a Spanish book "Hola" with content:
            Hola. Tengo un gato.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Tengo/ /un/ /gato/.
        Given I visit "/"
        When I set the book table filter to "Hola"
        Then the book table contains:
            Hola; Spanish; ; 4; ; …

    # Dealing with production bug.
    Scenario: Japanese book with multiple paragraphs works.
        Given I visit "/"
        Given a Japanese book "Jp test" with content:
            多くなったのは初めてです。
            
            韓国から来た人。
        Then the page title is Reading "Jp test"

    # Dealing with production bug.
    Scenario: Japanese book unique constraint failed bug.
        Given I visit "/"
        Given a Japanese book "Jp test" with content:
            情報さえ集めればどんどんお金も集まってくる。
        Then the page title is Reading "Jp test"
        And the reading pane shows:
            情報/さえ/集めれ/ば/どんどん/お金/も/集まっ/て/くる/。

    # Sanity check import same sequence of chars twice.
    Scenario: Japanese import same text twice sanity check.
        Given I visit "/"
        Given a Japanese book "Jp test1" with content:
            情報さえ集めればどんどんお金も集まってくる。
        Then the page title is Reading "Jp test1"
        And the reading pane shows:
            情報/さえ/集めれ/ば/どんどん/お金/も/集まっ/て/くる/。

        Given a Japanese book "Jp test2" with content:
            情報さえ集めればどんどんお金も集まってくる。
        Then the page title is Reading "Jp test2"
        And the reading pane shows:
            情報/さえ/集めれ/ば/どんどん/お金/も/集まっ/て/くる/。

        When I click "集めれ" and edit the form:
            translation: hi
            status: 2
        Then the reading pane shows:
            情報/さえ/集めれ (2)/ば/どんどん/お金/も/集まっ/て/くる/。

        Given a Japanese book "Jp test3" with content:
            集めれ。
        Then the page title is Reading "Jp test3"
        And the reading pane shows:
            集め/れ/。


    # Production bug https://github.com/jzohrab/lute-v3/issues/375
    Scenario: Japanese production bug 375.
        Given I visit "/"
        Given a new Japanese term:
            text: だけど
            translation: but
        Given a Japanese book "Jp test" with content:
            最初はね難しい。

            だけども、間違えますよね。
        Then the page title is Reading "Jp test"
        And the reading pane shows:
            最初/はね/難しい/。/

            だけど (1)/も/、/間違え/ます/よ/ね/。
