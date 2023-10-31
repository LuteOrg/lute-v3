Feature: User can actually read and stuff.
    Text is rendered correctly, user can click on terms
    and define extra data.

    Background:
        Given a running site
        And demo languages

    Scenario: Book elements are rendered correctly
        When I create a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola (1/1)"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.

    Scenario: Updating term status updates the reading frame
        When I create a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola (1/1)"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.
        When I click "Hola" and edit the form:
            translation: Hello
            status: 2
        Then the reading pane shows:
            Hola (2)/. /Adios/ /amigo/.