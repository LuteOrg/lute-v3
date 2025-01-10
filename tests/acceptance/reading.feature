Feature: User can actually read and stuff.
    Text is rendered correctly, user can click on terms
    and define extra data.

    Background:
        Given a running site
        And demo languages


    @mobile
    Scenario: Book elements are rendered correctly
        Given a Spanish book "Hola" with content:
            Hola. Adios amigo.
        Then the page title is Reading "Hola"
        And the reading pane shows:
            Hola/. /Adios/ /amigo/.


    @mobile
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

        When I press hotkey "escape"
        And I click "Hola" and press hotkey "5"
        Then the reading pane shows:
            Hola (5)/. /Adios/ /amigo/.

        When I press hotkey "escape"
        When I click "Hola" and press hotkey "i"
        Then the reading pane shows:
            Hola (98)/. /Adios/ /amigo/.

        When I press hotkey "escape"
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


    Scenario: Edit forms are shown at appropriate times
        Given a Spanish book "Hola" with content:
            Tengo un amigo y una bebida.

        When I click "amigo"
        Then the reading page term form shows term "amigo"
        When I shift-drag from "Tengo" to "un"
        Then the reading page term form shows term "amigo"

        When I shift click:
            una
            bebida
        Then the bulk edit term form is shown
        When I press hotkey "1"
        Then the term form is hidden

        When I drag from "una" to "bebida"
        Then the reading page term form shows term "una bebida"

        When I press hotkey "escape"
        Then the term form is hidden

        When I drag from "una" to "bebida"
        Then the reading page term form shows term "una bebida"
        When I shift-drag from "Tengo" to "un"
        Then the reading page term form shows term "una bebida"


    Scenario: Bulk editing terms while reading
        Given a Spanish book "Hola" with content:
            Tengo otro amigo.
        When I shift click:
            amigo
            Tengo
        And I edit the bulk edit form:
            parent: gato
            change status: true
            status: 4
            add tags: hello, hi
        Then the reading pane shows:
            Tengo (4)/ /otro/ /amigo (4)/.
        Then the term table contains:
            ; Tengo; gato; ; Spanish; hello, hi; Learning (4)
            ; amigo; gato; ; Spanish; hello, hi; Learning (4)
            ; gato; ; ; Spanish; ; Learning (4)

        Given a Spanish book "Nuevo" with content:
            Tengo otro amigo.
        When I shift click:
            amigo
            otro
        And I edit the bulk edit form:
            remove parents: true
            change status: true
            status: 3
            add tags: newtag
            remove tags: hello, badtag
        Then the reading pane shows:
            Tengo (4)/ /otro (3)/ /amigo (3)/.
        Then the term table contains:
            ; Tengo; gato; ; Spanish; hello, hi; Learning (4)
            ; amigo; ; ; Spanish; hi, newtag; Learning (3)
            ; gato; ; ; Spanish; ; Learning (4)
            ; otro; ; ; Spanish; newtag; Learning (3)


    Scenario: Up and down arrow sets status
        Given a Spanish book "Hola" with content:
            Tengo un amigo.
        When I click "Tengo" and press hotkey "1"
        When I click "un" and press hotkey "2"
        When I click "amigo" and press hotkey "3"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/.

        When I press hotkey "escape"
        And I shift click:
            Tengo
            un
            amigo
        And I press hotkey "arrowup"
        Then the reading pane shows:
            Tengo (2)/ /un (3)/ /amigo (4)/.

        When I press hotkey "escape"
        And I shift click:
            Tengo
            un
            amigo
        When I press hotkey "arrowup"
        Then the reading pane shows:
            Tengo (3)/ /un (4)/ /amigo (5)/.

        When I press hotkey "escape"
        And I shift click:
            Tengo
            un
            amigo
        When I press hotkey "arrowup"
        Then the reading pane shows:
            Tengo (4)/ /un (5)/ /amigo (99)/.

        When I press hotkey "escape"
        And I shift click:
            Tengo
            un
            amigo
        When I press hotkey "arrowup"
        Then the reading pane shows:
            Tengo (5)/ /un (99)/ /amigo (99)/.

        When I press hotkey "escape"
        And I shift click:
            Tengo
            un
            amigo
        When I press hotkey "arrowdown"
        Then the reading pane shows:
            Tengo (4)/ /un (5)/ /amigo (5)/.

        When I press hotkey "escape"
        And I click "Tengo" and press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        And I press hotkey "arrowdown"
        Then the reading pane shows:
            Tengo (1)/ /un (5)/ /amigo (5)/.


    Scenario: Toggling highlighting only shows highlights on hovered terms
        Given a Spanish book "Hola" with content:
            Tengo un amigo y otro.
        When I click "Tengo" and press hotkey "1"
        Then the reading pane shows:
            Tengo (1)/ /un/ /amigo/ /y/ /otro/.
        When I click "un" and press hotkey "2"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo/ /y/ /otro/.
        When I click "amigo" and press hotkey "3"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/ /y/ /otro/.
        When I press hotkey "h"
        And I hover over "Tengo"
        Then the reading pane shows:
            Tengo (1)/ /un/ /amigo/ /y/ /otro/.
        When I press hotkey "h"
        And I press hotkey "m"
        And I press hotkey "m"
        Then the reading pane shows:
            Tengo (1)/ /un (2)/ /amigo (3)/ /y/ /otro/.


    # DISABLING TEST, can't figure out what is wrong.
    # When a book has multiple pages, the hotkey actions during
    # acceptance testing somehow seem "stuck" on page 1.
    #
    # i.e. if I'm on page 1, and hit the "hotkey_MarkRead",
    # the page does go to page 2, and the hidden control
    # "#page_num" is updated to 2; however, subsequent calls
    # to handle_page_done() (in read/index.html) **always** post
    # the pagenum as 1, even though it should read from the field
    # parseInt($('#page_num').val()).
    #
    # The hotkeys work correctly when run from the browser,
    # so either:
    # * something is wrong how selenium runs the browser/js
    # * I'm not simulating the keypress correctly
    # * there's _somehow_ some weird state being held on to.
    #
    ### Scenario: Can use hotkeys to move to next pages
    ###     Given I set hotkey "hotkey_MarkRead" to "Digit8"
    ###     And I set hotkey "hotkey_MarkReadWellKnown" to "Digit9"
    ###     And a Spanish book "Hola" with content:
    ###         Tengo una GATITA.
    ###         ---
    ###         Tengo una bebida.
    ###         ---
    ###         Tengo LAAAAAAA BEBIDA.
    ###     Then the reading pane shows:
    ###         Tengo/ /una/ /GATITA/.

    ###     When I press hotkey "8"
    ###     And sleep for 2
    ###     Then the reading pane shows:
    ###         Tengo/ /una/ /bebida/.
    ###     And book pages with read dates are:
    ###         Hola; 1

    ###     When I press hotkey "9"
    ###     Then the reading pane shows:
    ###         Tengo (99)/ /LAAAAAAA/ /BEBIDA (99)/.
    ###     And book pages with read dates are:
    ###         Hola; 1
    ###         Hola; 2


    Scenario: Can use hotkeys to go to previous and next pages
        Given I set hotkey "hotkey_PreviousPage" to "Digit8"
        And I set hotkey "hotkey_NextPage" to "Digit9"
        And a Spanish book "Hola" with content:
            one.
            ---
            two.
        Then the reading pane shows:
            one/.

        When I press hotkey "9"
        Then the reading pane shows:
            two/.
        And book pages with read dates are:
            -

        When I press hotkey "8"
        Then the reading pane shows:
            one/.
        And book pages with read dates are:
            -


    Scenario: Can use hotkeys to mark the page as read
        Given I set hotkey "hotkey_MarkRead" to "Digit8"
        And a Spanish book "Hola" with content:
            Tengo una GATITA.
            ---
            Tengo una bebida.
        Then the reading pane shows:
            Tengo/ /una/ /GATITA/.

        When I press hotkey "8"
        Then the reading pane shows:
            Tengo/ /una/ /bebida/.
        And book pages with read dates are:
            Hola; 1

    Scenario: Can use hotkeys to mark unknown terms as known and the page as read
        Given I set hotkey "hotkey_MarkReadWellKnown" to "Digit9"
        And a Spanish book "Hola" with content:
            Tengo una GATITA.
            ---
            Tengo una bebida.
        Then the reading pane shows:
            Tengo/ /una/ /GATITA/.

        When I press hotkey "9"
        Then the reading pane shows:
            Tengo (99)/ /una (99)/ /bebida/.
        And book pages with read dates are:
            Hola; 1


    Scenario: Page start date is set correctly during reading
        Given a Spanish book "Hola" with content:
            page one here.
            ---
            two.
            ---
            three.
        Then book pages with start dates are:
            Hola; 1
        And the reading pane shows:
            page/ /one/ /here/.

        Given all page start dates are set to null
        Then book pages with start dates are:
            -

        # Single form post:
        When I click "page" and edit the form:
            text: page
        Then the reading pane shows:
            page (1)/ /one/ /here/.
        And book pages with start dates are:
            -

        # Bulk edit:
        When I press hotkey "escape"
        And I shift click:
            one
            here
        And I edit the bulk edit form:
            change status: true
            status: 3
        Then the reading pane shows:
            page (1)/ /one (3)/ /here (3)/.
        And book pages with start dates are:
            -

        # Hotkey:
        When I press hotkey "escape"
        And I click "here" and press hotkey "2"
        Then the reading pane shows:
            page (1)/ /one (3)/ /here (2)/.
        And book pages with start dates are:
            -

        # Bulk update with hotkey:
        When I press hotkey "escape"
        And I shift click:
            page
            one
        When I press hotkey "arrowup"
        Then the reading pane shows:
            page (2)/ /one (4)/ /here (2)/.
        And book pages with start dates are:
            -

        When I press hotkey "escape"
        And I shift click:
            one
            here
        When I press hotkey "1"
        Then the reading pane shows:
            page (2)/ /one (1)/ /here (1)/.
        And book pages with start dates are:
            -

        When I go to the next page
        Then the reading pane shows:
            two/.
        And book pages with start dates are:
            Hola; 2

        When I go to the previous page
        Then the reading pane shows:
            page (2)/ /one (1)/ /here (1)/.
        And book pages with start dates are:
            Hola; 1
            Hola; 2

        Given all page start dates are set to null
        Then book pages with start dates are:
            -

        When I click the footer next page
        Then the reading pane shows:
            two/.
        And book pages with start dates are:
            Hola; 2

        Given all page start dates are set to null
        Then book pages with start dates are:
            -

        When I click the footer green check
        Then the reading pane shows:
            three/.
        And book pages with start dates are:
            Hola; 3


    # Issue 530: "peeking" at page doesn't set page data.
    Scenario: Peeking at page does not set current page or start date.
        Given a Spanish book "Hola" with content:
            Uno.
            ---
            Dos.
        Then the reading pane shows:
            Uno/.
        And book pages with start dates are:
            Hola; 1

        Given I peek at page 2
        Then the reading pane shows:
            Dos/.
        And book pages with start dates are:
            Hola; 1

        Given I visit "/"
        When I set the book table filter to "Hola"
        Then the book table contains:
            Hola; Spanish; ; 2;
