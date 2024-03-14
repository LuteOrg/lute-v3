Feature: User can actually read and stuff.
    Text is rendered correctly, user can click on terms
    and define extra data.

    Background:
        Given a running site
        And demo languages


    Scenario: Book elements are rendered correctly
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.


    Scenario: Updating term status updates the reading frame
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


    Scenario: Reading a Japanese book
        Given a Japanese book "Genki" with content:
            私は元気です.
        Then the page title is Reading "Genki"
        And the reading pane shows:
            私/は/元気/です/.
        When I click "元気" and edit the form:
            translation: genki
            status: 2
        Then the reading pane shows:
            私/は/元気 (2)/です/.


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


# TODO restore test: was getting "Message: stale element reference: stale element not found"
# error on trying to click the green check, couldn't solve this quickly.
###    Scenario: Click footer green checkmark ("mark rest as known") sets rest to 99.
###        Given a Spanish book "Hola" with content:
###            Hola. Adios amigo.
###        When I click "Hola" and press hotkey "1"
###        Then the reading pane shows:
###            Hola (1)/. /Adios/ /amigo/.
###        When I click the footer green check
###        Then the reading pane shows:
###            Hola (1)/. /Adios (99)/ /amigo (99)/.


    Scenario: Learned terms are applied to new texts.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        When I click "amigo" and press hotkey "1"
        Then the reading pane shows:
            Hola/. /Adios/ /amigo (1)/.
        Given a Spanish book "Otro" with content:
            Tengo otro amigo.
        Then the reading pane shows:
            Tengo/ /otro/ /amigo (1)/.


# TODO fix broken test: this test failed frequently in github ci, but never locally.
###    Scenario: Clicking next w/ checkmark or next in footer sets bookmark
###        Given the demo stories are loaded
###        When I click the "Tutorial" link
###        And I click the footer next page
###        And sleep for 2
###        Given I visit "/"
###        And I clear the book filter
###        And the book table loads "Tutorial (2/6)"
###        # .... nothing more to check ...


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

        # TODO fix_flaky_test: this would periodically fail the
        # assertion, "cap." still had status 2.
        ### When I click "He" and edit the form:
        ###     parents: [ 'cap.' ]
        ### And sleep for 1
        ### And I hover over "He"
        ### And I press hotkey "3"
        ### And sleep for 1
        ### Then the reading pane shows:
        ###     He (3)/ /escrito/ /cap. (3)/ /uno/.


    Scenario: User can update the text while reading.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.
        When I change the current text content to:
            Tengo otro amigo.
        Then the reading pane shows:
            Tengo/ /otro/ /amigo/.


    Scenario: User can add and remove pages.
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.

        When I add a page after current with content:
            Nuevo.
        Then the reading pane shows:
            Nuevo/.
        When I go to the previous page
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.

        When I add a page before current with content:
            Viejo.
        Then the reading pane shows:
            Viejo/.
        When I go to the next page
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.
        When I go to the next page
        Then the reading pane shows:
            Nuevo/.

        When I delete the current page
        Then the reading pane shows:
            Hola/. /Adios/ /amigo/.


    Scenario: Hotkey affects hovered element
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I hover over "otro"
        And sleep for 1
        And I press hotkey "1"
        And sleep for 1
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


    Scenario: Up and down arrow sets status
        Given a Spanish book "Hola" with content:
            Tengo un amigo.
        When I click "Tengo" and press hotkey "1"
        When I click "un" and press hotkey "2"
        When I click "amigo" and press hotkey "3"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/.

        When I shift click:
            Tengo
            un
            amigo
        And I press hotkey "UP"
        Then the reading pane shows:
            Tengo (2)/ /un (3)/ /amigo (4)/.

        When I shift click:
            Tengo
            un
            amigo
        When I press hotkey "UP"
        Then the reading pane shows:
            Tengo (3)/ /un (4)/ /amigo (5)/.

        When I shift click:
            Tengo
            un
            amigo
        When I press hotkey "UP"
        Then the reading pane shows:
            Tengo (4)/ /un (5)/ /amigo (99)/.

        When I shift click:
            Tengo
            un
            amigo
        When I press hotkey "UP"
        Then the reading pane shows:
            Tengo (5)/ /un (99)/ /amigo (99)/.

        When I shift click:
            Tengo
            un
            amigo
        When I press hotkey "DOWN"
        Then the reading pane shows:
            Tengo (4)/ /un (5)/ /amigo (5)/.

        When I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        And I click "Tengo" and press hotkey "DOWN"
        Then the reading pane shows:
            Tengo (1)/ /un (5)/ /amigo (5)/.


    Scenario: Toggling highlighting only shows highlights on hovered terms
        Given a Spanish book "Hola" with content:
            Tengo un amigo y otro.
        When I click "Tengo" and press hotkey "1"
        When I click "un" and press hotkey "2"
        When I click "amigo" and press hotkey "3"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/ /y/ /otro/.
        When I press hotkey "h"
        Then the reading pane shows:
            Tengo/ /un/ /amigo/ /y/ /otro/.
        When I hover over "Tengo"
        Then the reading pane shows:
            Tengo (1)/ /un/ /amigo/ /y/ /otro/.
        When I press hotkey "h"
        And I press hotkey "m"
        And I press hotkey "m"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/ /y/ /otro/.
