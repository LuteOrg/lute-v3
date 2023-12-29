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

    Scenario: I can import a text file.
        Given I visit "/"
        Given a Spanish book "Hola" from file hola.txt
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Tengo/ /un/ /amigo/.

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
            Hola; Spanish; ; 4 (0%);

    # Dealing with production bug.
    Scenario: Japanese book with multiple paragraphs works.
        Given I visit "/"
        Given a Japanese book "Jp test" with content:
            多くなったのは初めてです。
            
            韓国から来た人。
        Then the page title is Reading "Jp test"
