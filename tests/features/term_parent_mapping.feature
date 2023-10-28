Feature: Term import
    Valid files are imported

    Background:
        Given demo data
        And language Spanish

    # The scenarios here use parent term 'dog' and child term 'dogs',
    # as documented in the wiki.
    # https://github.com/jzohrab/lute/wiki/Bulk-Mapping-Parent-Terms.
    # The wiki is actually slightly out of date, as Lute now supports
    # multiple parents.


    Scenario: "dog" and "dogs" exist, "dogs" doesn't have a parent.
        Given terms:
            dog
            dogs
        Then parents should be:
            -
        Given import file:
            parent,term
            dog,dogs
        Then import should succeed with 0 created, 1 updated
        And parents should be:
            dog; dogs


    Scenario: "dog" and "dogs" exist, "dog" is already parent of "dogs"
        Given terms:
            dog
            dogs
        And "dog" is parent of "dogs"
        Then parents should be:
            dog; dogs
        Given import file:
            parent,term
            dog,dogs
        Then import should succeed with 0 created, 0 updated
        # Unchanged parents
        And parents should be:
            dog; dogs
        And words table should contain:
            dog
            dogs


    Scenario: "dog" and "dogs" exist, "dogs" already has a parent, so a new parent is added
        Given terms:
            dog
            dogs
            hound
        And "hound" is parent of "dogs"
        Then parents should be:
            hound; dogs
        Given import file:
            parent,term
            dog,dogs
        Then import should succeed with 0 created, 1 updated
        # Unchanged parents
        And parents should be:
            dog; dogs
            hound; dogs
        And words table should contain:
            dog
            dogs
            hound


    Scenario: Mapping a term as its own parent does nothing
        Given terms:
            dog
            dogs
        Given import file:
            parent,term
            dogs,dogs
        Then import should succeed with 0 created, 0 updated
        And parents should be:
            -


    Scenario: "dogs" exist but "dog" does not
        Given terms:
            dogs
        And import file:
            parent,term
            dog,dogs
        Then import should succeed with 1 created, 1 updated
        And parents should be:
            dog; dogs
        And words table should contain:
            dog
            dogs
        And "dog" flash message should be:
            Auto-created parent for "dogs"


    Scenario: "doggies" and "dogs" exist but "dog" does not
        Given terms:
            dogs
            doggies
        And import file:
            parent,term
            dog,dogs
            dog,doggies
        Then import should succeed with 1 created, 2 updated
        And parents should be:
            dog; doggies
            dog; dogs
        And words table should contain:
            dog
            doggies
            dogs
        And "dog" flash message should be:
            Auto-created parent for "dogs" + 1 more
        And "doggies" flash message should be:
            -


    Scenario: Import does not create new terms if missing child and parent
        Given import file:
            parent,term
            dog,dogs
        Then import should succeed with 0 created, 0 updated
        And words table should contain:
            -


    Scenario: "dogs" exist but "dog" does not, no "cat" terms exist
        Given terms:
            dogs
        And import file:
            parent,term
            dog,dogs
            cat,cats
        Then import should succeed with 1 created, 1 updated
        And parents should be:
            dog; dogs
        And words table should contain:
            dog
            dogs
        And "dog" flash message should be:
            Auto-created parent for "dogs"


    Scenario: "dog" exists but "dogs" child term does not
        Given terms:
            dog
        And import file:
            parent,term
            dog,dogs
        Then import should succeed with 1 created, 0 updated
        And words table should contain:
            dog
            dogs
        And parents should be:
            dog; dogs
        And "dogs" flash message should be:
            Auto-created and mapped to parent "dog"


    Scenario: Duplicate mappings are ok
        Given terms:
            dog
        And import file:
            parent,term
            dog,dogs
            dog,dogs
        Then import should succeed with 1 created, 0 updated
        And words table should contain:
            dog
            dogs
        And parents should be:
            dog; dogs
        And "dogs" flash message should be:
            Auto-created and mapped to parent "dog"


    Scenario: Child term can be mapped to multiple parents.
        Given terms:
            dogs
        And import file:
            parent,term
            dog,dogs
            pup,dogs
        Then import should succeed with 2 created, 2 updated
        And words table should contain:
            dog
            dogs
            pup
        And parents should be:
            dog; dogs
            pup; dogs


    Scenario: Case ignored for mapping, and accented caps is OK.
        Given terms:
            pA
            Á
        Then words table should contain:
            pa
            á
        Given import file:
            parent,term
            pA,á
        Then import should succeed with 0 created, 1 updated
        And parents should be:
            pa; á


    Scenario: Existing term and parent, new link created
        Given terms:
            dog
            dogs
        And import file:
            parent,term
            dog,dogs
        Then import should succeed with 0 created, 1 updated
        And parents should be:
            dog; dogs
        And "dogs" flash message should be:
            -


    Scenario: Child term creates parent term which creates other child term - "propagation" of new terms
        Given terms:
            gatito
        # Note for the file below, "gatito" creates "gato", but then "gato" creates "gatos"!
        And import file:
            parent,term
            gato,gatos
            gato,gatito
        Then import should succeed with 2 created, 1 updated
        And words table should contain:
            gatito
            gato
            gatos
        And parents should be:
            gato; gatito
            gato; gatos


     # Tricky case where a new term will get created, but is also
     # needed as a parent for an existing term ... this showed up on
     # tests on my machine.
     Scenario: new term is used as parent for other term
        Given terms:
            aladas
            alado
        # x is a (new) parent of aladas, _and_ a (new)
        # child of alado.
        And import file:
            parent,term
            x,aladas
            alado,x
        Then import should succeed with 1 created, 2 updated
        And words table should contain:
            aladas
            alado
            x
        And parents should be:
            alado; x
            x; aladas


    Scenario: Bad heading throws
        Given import file:
            blah,blah2
            blah,gato,x
        Then import should fail with message:
            File must contain headings 'parent' and 'term'


    Scenario: Term is required
        Given import file:
            parent,term
            something,
        Then import should fail with message:
            Term is required


    Scenario: Parent is required
        Given import file:
            parent,term
            ,something
        Then import should fail with message:
            Term is required


    Scenario: Empty file throws
        Given empty import file
        Then import should fail with message:
            No mappings in file


    Scenario: File with only headings throws
        Given import file:
            parent,term
        Then import should fail with message:
            No mappings in file