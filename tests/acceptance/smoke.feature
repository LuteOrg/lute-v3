Feature: Smoke test.
    Create a book, read it and create terms, view term list, export CSV.

    Background:
        Given a running site
        And demo languages


    Scenario: Smoke test
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.

        When I click "Hola" and edit the form:
            translation: Hello
            status: 2
        Then the reading pane shows:
            Hola (2)/. /Adios/ /amigo/.

        When I click "Adios" and press hotkey "1"
        Then the reading pane shows:
            Hola (2)/. /Adios (1)/ /amigo/.

        Then the term table contains:
            ; Adios; ; ; Spanish; ; New (1)
            ; Hola; ; Hello; Spanish; ; New (2)

        When click Export CSV
        And sleep for 1
        Then exported CSV file contains:
            term,parent,translation,language,tags,status,link_status
            Adios,,,Spanish,,1,
            Hola,,Hello,Spanish,,2,
