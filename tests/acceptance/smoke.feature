Feature: Smoke test.
    Create a book, read it and create terms, view term list, export CSV.

    Background:
        Given a running site
        And demo languages


    Scenario: Smoke test
        # Book created and loaded.
        Given a Spanish book "Hola" with content:
            Hola, adios amigo.

        # No terms listed yet.
        Given I visit "/"
        Then the term table contains:
            -

        # On read, still no terms shown in listing.
        Given I visit "/"
        When I click the "Hola" link
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/, /adios/ /amigo/.

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
            Hola (2)/, /adios/ /amigo/.

        When I click "adios" and press hotkey "1"
        Then the reading pane shows:
            Hola (2)/, /adios (1)/ /amigo/.

        # Now terms exist.
        Then the term table contains:
            ; Hola; ; Hello; Spanish; ; New (2)
            ; adios; ; ; Spanish; ; New (1)

        # Only listed terms included.
        When click Export CSV
        And sleep for 1
        Then exported CSV file contains:
            term,parent,translation,language,tags,added,status,link_status,pronunciation
            Hola,,Hello,Spanish,,DATE_HERE,2,,
            adios,,,Spanish,,DATE_HERE,1,,

        # DISABLING this for now: when the page is rendered,
        # unknown terms are created with status = 0.  Creating
        # the same term from the term form causes an integrity error.
        ### Given a new Spanish term:
        ###     text: amigo
        ###     translation: friend
        ###     status: 4
        ### When I click the "amigo" link

        ### # Term has been updated in reading screen.
        ### Given I visit "/"
        ### When I click the "Hola" link
        ### Then the page title is Reading "Hola"
        ### And the reading pane shows:
        ###     Hola (2)/. /Adios (1)/ /amigo (4)/, /adios (1)/.
