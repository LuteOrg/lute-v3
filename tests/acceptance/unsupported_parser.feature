Feature: Unsupported language data is hidden

    Background:
        Given a running site
        And demo languages
        And the demo stories are loaded

        Given a new Spanish term:
            text: gato
            translation: cat
        And a Spanish book "Hola" with content:
            Hola. Tengo un gato.
        And a Japanese book "Hola" with content:
            こんにちは
        And a new Japanese term:
            text: gato
            translation: cat


    Scenario: Disabled data is hidden
        Given I disable the "japanese" parser
        Given I visit "/"

        When I set the book table filter to "Hola"
        Then the book table contains:
            Hola; Spanish; ; 4; ; …
        Then the term table contains:
            ; gato; ; cat; Spanish; ; New (1)


    Scenario: Re-enabled data is still available
        Given I disable the "japanese" parser
        Given I visit "/"
        Given I enable the "japanese" parser
        Given I visit "/"

        When I set the book table filter to "Hola"
        Then the book table contains:
            Hola; Japanese; ; 1; ; …
            Hola; Spanish; ; 4; ; …
        Then the term table contains:
            ; gato; ; cat; Japanese; ; New (1)
            ; gato; ; cat; Spanish; ; New (1)
