Feature: Books and stats are available

    Background:
        Given a running site
        And demo languages

    Scenario: Books and stats are shown on the first page.
        Given a Spanish book "Hola" with content:
            Hola. Tengo un gato.
        Then the page title is Reading "Hola (1/1)"
        And the reading pane shows:
            Hola/. /Tengo/ /un/ /gato/.
        Given I visit "/"
        When I set the book table filter to "Hola"
        Then the book table contains:
            Hola; Spanish; ; 4 (0%);
