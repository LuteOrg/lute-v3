Feature: User can actually read and stuff.
    Text is rendered correctly, user can click on terms
    and define extra data.

    Background:
        Given a running site
        And demo languages


    Scenario: Book elements are rendered correctly
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola (1/1)"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.


    Scenario: Updating term status updates the reading frame
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola (1/1)"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.
        When I click "Hola" and edit the form:
            translation: Hello
            status: 2
        Then the reading pane shows:
            Hola (2)/. /Adios/ /amigo/.


    Scenario: Changing term case in form is allowed
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "Hola" and edit the form:
            text: HOLA
        Then the reading pane shows:
            Hola (1)/. /Adios/ /amigo/.


    Scenario: Cannot change term text
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "Hola" and edit the form:
            text: new_text
        Then the reading page term form frame contains "Can only change term case"


    Scenario: Pressing a hotkey updates a term's status
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "Hola" and press hotkey "1"
        Then the reading pane shows:
            Hola (1)/. /Adios/ /amigo/.
        When I click "Hola" and press hotkey "5"
        Then the reading pane shows:
            Hola (5)/. /Adios/ /amigo/.
        When I click "Hola" and press hotkey "i"
        Then the reading pane shows:
            Hola (98)/. /Adios/ /amigo/.
        When I click "Hola" and press hotkey "w"
        Then the reading pane shows:
            Hola (99)/. /Adios/ /amigo/.


    Scenario: Click footer green checkmark ("mark rest as known") sets rest to 99.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "Hola" and press hotkey "1"
        Then the reading pane shows:
            Hola (1)/. /Adios/ /amigo/.
        When I click the footer green check
        Then the reading pane shows:
            Hola (1)/. /Adios (99)/ /amigo (99)/.


    Scenario: Learned terms are applied to new texts.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "Hola" and press hotkey "1"
        And I click the footer green check
        Then the reading pane shows:
            Hola (1)/. /Adios (99)/ /amigo (99)/.
        Given a Spanish book "Otro" with content:
            Tengo otro amigo.
        Then the reading pane shows:
            Tengo/ /otro/ /amigo (99)/.


    Scenario: Clicking next w/ checkmark or next in footer sets bookmark
        Given the demo stories are loaded
        When I click the "Tutorial" link
        # The green check doesn't advance the page
        And I click the footer green check
        And I click the footer next page
        Given I visit "/"
        And the book table loads "Tutorial"
        Then the page contains "Tutorial (2/"


     Scenario: Language split sentence exceptions are respected
        Given I update the Spanish language:
            exceptions_split_sentences: cap.
        And a Spanish book "Hola" with content:
            He escrito cap. uno.
        Then the reading pane shows:
            He/ /escrito/ /cap./ /uno/.
        When I click "cap." and edit the form:
            status: 2
        Then the reading pane shows:
            He/ /escrito/ /cap. (2)/ /uno/.
        When I click "He" and edit the form:
            parents: [ 'cap.' ]
        Then the reading pane shows:
            He (1)/ /escrito/ /cap. (2)/ /uno/.


    Scenario: User can update the text while reading.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.
        When I change the current text content to:
            Tengo otro amigo.
        Then the reading pane shows:
            Tengo/ /otro/ /amigo/.


    Scenario: Hotkey affects hovered element
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I hover over "otro"
        And I press hotkey "1"
        Then the reading pane shows:
            Tengo/ /otro (1)/ /amigo/.


    Scenario: Clicked word "keeps the focus"
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I click "amigo"
        And I hover over "otro"
        And I press hotkey "1"
        Then the reading pane shows:
            Tengo/ /otro/ /amigo (1)/.


    Scenario: Clicking an already-clicked word releases the focus
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I click "amigo"
        And I click "amigo"
        And I hover over "otro"
        And I press hotkey "1"
        Then the reading pane shows:
            Tengo/ /otro (1)/ /amigo/.


    Scenario: Shift-click selects multiple words
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I shift click:
            amigo
            Tengo
        And I press hotkey "1"
        Then the reading pane shows:
            Tengo (1)/ /otro/ /amigo (1)/.
