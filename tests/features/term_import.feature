Feature: Term import
    Valid files are imported

    Background:
        Given demo data


    Scenario: Smoke test with no create or update
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create false, update false
        Then import should succeed with 0 created, 0 updated, 1 skipped
        And words table should contain:
            -


    Scenario: Smoke test with create only
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Import new term as unknown
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false, new as unknown true
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus from words order by WoText" should return:
            gato; 0


    Scenario: Smoke test updates ignored if not updating
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun

        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,NEW,,1,NEW,NEW
        When import with create true, update false
        Then import should succeed with 0 created, 0 updated, 1 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Smoke test with update only
        Given import file:
            language,term,translation,status,tags,pronunciation
            Spanish,gato,cat,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped

        Given import file:
            language,term,translation,status,tags
            Spanish,gato,cat,3,fuzzy
            Spanish,perro,dog,3,fuzzy
        When import with create false, update true
        Then import should succeed with 0 created, 1 updated, 1 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 3
            parents: -
            tags: fuzzy


    Scenario: Smoke test with both create and update
        Given import file:
            language,term,translation,status,tags,pronunciation
            Spanish,gato,cat,1,"animal, noun",GA-toh
        When import with create true, update true
        Then import should succeed with 1 created, 0 updated, 0 skipped

        Given import file:
            language,term,translation,status,tags
            Spanish,gato,cat,3,fuzzy
            Spanish,perro,dog,2,fuzzy
        When import with create true, update true
        Then import should succeed with 1 created, 1 updated, 0 skipped
        And words table should contain:
            gato
            perro
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 3
            parents: -
            tags: fuzzy
        And Spanish term "perro" should be:
            translation: dog
            pronunciation: -
            status: 2
            parents: -
            tags: fuzzy


    Scenario: Translation field can contain a return
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,"A cat.
            A house cat.",,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: A cat.
            A house cat.
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Multiple terms with returns in translations
        # This doesn't really test anything, sanity check only.
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,term,"this is a trans
            1. something
            2. ok",,1,"a, b",
            Spanish,other,"another thing:
            1. blah
            2. ""you know""",,3,,TEE-2
            Spanish,third,,,W,?,
        When import with create true, update false
        Then import should succeed with 3 created, 0 updated, 0 skipped
        And words table should contain:
            other
            term
            third


    Scenario: Smoke test with two terms
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
            Spanish,perro,dog,,1,"animal, noun",PERR-oh
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            perro


    Scenario: Existing terms should not change
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,UPDATED,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 0 created, 0 updated, 1 skipped
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Import is case-insensitive
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,GATO,UPDATED,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 0 created, 0 updated, 1 skipped


    Scenario: Import statuses are mapped to status IDs
        Given import file:
            language,term,status
            Spanish,a,1
            Spanish,b,2
            Spanish,c,3
            Spanish,d,4
            Spanish,e,5
            Spanish,f,W
            Spanish,g,I
        When import with create true, update false
        Then import should succeed with 7 created, 0 updated, 0 skipped
        And words table should contain:
            a
            b
            c
            d
            e
            f
            g
        And sql "select WoText, WoStatus from words order by WoText" should return:
            a; 1
            b; 2
            c; 3
            d; 4
            e; 5
            f; 99
            g; 98


    Scenario: Import field names are case-insensitive
        Given import file:
            LANGUAGE,Term,TRANSLATION,paRENT,statUS,TAGS,Pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Parent created on import
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gatos,cat,gato,1,"animal, noun",GA-toh
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gatos
        And Spanish term "gatos" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: gato
            tags: animal, noun


    Scenario: Same term in different languages
        Given import file:
            language,term,parent
            Spanish,gatos,gato
            English,gato,
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gato
            gatos
        And Spanish term "gatos" should be:
            translation: -
            pronunciation: -
            status: 1
            parents: gato
            tags: -


    Scenario: Parent in same import file gets its own data
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gatos,,gato,1,,
            Spanish,gato,CAT,,1,animal,GAH-toh
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gatos
        And Spanish term "gatos" should be:
            translation: -
            pronunciation: -
            status: 1
            parents: gato
            tags: -
        And Spanish term "gato" should be:
            translation: CAT
            pronunciation: GAH-toh
            status: 1
            parents: -
            tags: animal


    Scenario: Import can sync parent and children statuses
        Given import file:
            language,term,parent,status
            Spanish,a,,1
            Spanish,b,a,2
            Spanish,c,a,3
            Spanish,d,a,4
        When import with create true, update false
        Then import should succeed with 4 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 1; 0
            b; 2; 0
            c; 3; 0
            d; 4; 0

        Given import file:
            language,term,parent,status,link_status
            Spanish,a,,1,
            Spanish,b,a,2,y
            Spanish,c,a,3,y
            Spanish,d,a,4
        When import with create false, update true
        Then import should succeed with 0 created, 4 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0
            b; 3; 1
            c; 3; 1
            d; 4; 0


    Scenario: Issue 387 child without status inherits parent status if linked
        Given import file:
            language,term,status
            Spanish,a,3
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0

        Given import file:
            language,term,parent,link_status
            Spanish,achild,a,y
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0
            achild; 3; 1


    Scenario: Issue 387 child with status overrides parent status if linked
        Given import file:
            language,term,status
            Spanish,a,3
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0

        Given import file:
            language,term,parent,status,link_status
            Spanish,achild,a,2,y
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 2; 0
            achild; 2; 1


    Scenario: Issue 387 importing an unknown child of a parent sets its status to parent
        Given import file:
            language,term,status
            Spanish,a,3
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0

        # Importing a term as "unknown" really imports it as "known" (with non-0 status)
        # if it's associated with a known parent!
        # This may seem counter-intuitive, but it's really the only thing that makes sense.
        # The parent is "known" (non-0 status), so if the child is associated with that
        # parent then really it's known too.  Having such a child be an exception to the
        # parent-status following rules is so hairy that I'm not going to bother doing it.
        Given import file:
            language,term,parent,link_status
            Spanish,achild,a,y
        When import with create true, update false, new as unknown true
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoStatus, WoSyncStatus from words order by WoText" should return:
            a; 3; 0
            achild; 3; 1

    
    Scenario: Import file fields can be in any order
        Given import file:
            language,translation,term,parent,status,tags,pronunciation
            Spanish,,gatos,gato,1,,
            Spanish,CAT,gato,,1,animal,GAH-toh
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gatos



    Scenario: Term can have multiple parents
        Given import file:
            language,translation,term,parent,status,tags,pronunciation
            Spanish,,gatos,"gato, cat",1,,
        When import with create true, update false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And words table should contain:
            cat
            gato
            gatos


    Scenario: Import file with only language and term
        Given import file:
            language,term
            Spanish,gato
            spanish,gatos
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gatos


    Scenario: Field named added is ignored
        Given import file:
            language,term,added
            Spanish,gato,27-July-2020
            spanish,gatos,27-July-2020
        When import with create true, update false
        Then import should succeed with 2 created, 0 updated, 0 skipped
        And words table should contain:
            gato
            gatos


    Scenario: Missing required field throws
        Given import file:
            language,thing
            blah,gato
        Then import should fail with message:
            Missing required field 'term'


    Scenario: Bad heading throws
        Given import file:
            language,term,junk
            blah,gato,x
        Then import should fail with message:
            Unknown field 'junk'


    Scenario: Invalid language throws
        Given import file:
            language,term
            blah,gato
        Then import should fail with message:
            Unknown language 'blah'


    Scenario: Duplicate term throws
        Given import file:
            language,term
            Spanish,gato
            Spanish,gato
        Then import should fail with message:
            Duplicate terms in import: Spanish: gato


    Scenario: Fix issue 51: mandarin duplicate term throws
        Given import file:
            language,term,translation,pronunciation,tags
            Classical chinese,啊 ,auxiliary word,a,HSK2
            Classical chinese,啊,ah,a,HSK4
        Then import should fail with message:
            Duplicate terms in import: Classical chinese: 啊


    Scenario: Bad status throws
        Given import file:
            language,term,status
            Spanish,gato,7
        Then import should fail with message:
            Status must be one of 1, 2, 3, 4, 5, I, W, or blank


    Scenario: Term is required
        Given import file:
            language,term,status
            Spanish,,7
        Then import should fail with message:
            Term is required


    Scenario: Empty file throws
        Given empty import file
        Then import should fail with message:
            No terms in file


    Scenario: File with only headings throws
        Given import file:
            language,term,status
        Then import should fail with message:
            No terms in file
