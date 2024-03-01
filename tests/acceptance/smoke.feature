Feature: Smoke test.
    Create a book, read it and create terms, view term list, export CSV.

    Background:
        Given a running site
        And demo languages


    Scenario: Smoke test
        # Book created and loaded.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo, adios.

        # No terms listed yet.
        Given I visit "/"
        Then the term table contains:
            -

        # On read, still no terms shown in listing.
        Given I visit "/"
        When I click the "Hola" link
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/, /adios/.

        # Still no terms listed.
        Given I visit "/"
        Then the term table contains:
            -

        Given I visit "/"
        When I click the "Hola" link
        And I click "Hola" and edit the form:
            translation: Hello
            status: 2
        Then the reading pane shows:
            Hola (2)/. /Adios/ /amigo/, /adios/.

        When I click "Adios" and press hotkey "1"
        Then the reading pane shows:
            Hola (2)/. /Adios (1)/ /amigo/, /adios (1)/.

        # Now terms exist.
        Then the term table contains:
            ; Adios; ; ; Spanish; ; New (1)
            ; Hola; ; Hello; Spanish; ; New (2)

        # Only listed terms included.
        When click Export CSV
        And sleep for 1
        Then exported CSV file contains:
            term,parent,translation,language,tags,status,link_status
            Adios,,,Spanish,,1,
            Hola,,Hello,Spanish,,2,

        # Can create a new term, which then updates the text.
        Given a new Spanish term:
            text: amigo
            translation: friend
            status: 4

        # Term has been updated in reading screen.
        Given I visit "/"
        When I click the "Hola" link
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola (2)/. /Adios (1)/ /amigo (4)/, /adios (1)/.
