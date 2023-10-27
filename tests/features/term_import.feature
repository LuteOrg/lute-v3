Feature: Term import
    Valid files are imported

    Background:
        Given demo data

    Scenario: Smoke test
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        Then import should succeed with 1 created, 0 skipped
        And words table should contain:
            gato
        And Spanish term "gato" should be:
            translation: cat
            pronunciation: GA-toh
            status: 1
            parents: -
            tags: animal, noun


    Scenario: Translation field can contain a return
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,"A cat.
            A house cat.",,1,"animal, noun",GA-toh
        Then import should succeed with 1 created, 0 skipped
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
        Then import should succeed with 3 created, 0 skipped
        And words table should contain:
            other
            term
            third


    Scenario: Smoke test with two terms
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
            Spanish,perro,dog,,1,"animal, noun",PERR-oh
        Then import should succeed with 2 created, 0 skipped
        And words table should contain:
            gato
            perro


    Scenario: Existing terms should not change
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        Then import should succeed with 1 created, 0 skipped
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
        Then import should succeed with 0 created, 1 skipped
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
        Then import should succeed with 1 created, 0 skipped
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
        Then import should succeed with 0 created, 1 skipped


    Scenario: Import is case-insensitive
        Given import file:
            language,term,status
            Spanish,a,1
            Spanish,b,2
            Spanish,c,3
            Spanish,d,4
            Spanish,e,5
            Spanish,f,W
            Spanish,g,I
        Then import should succeed with 7 created, 0 skipped
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


    Scenario: Parent created on import
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gatos,cat,gato,1,"animal, noun",GA-toh
        Then import should succeed with 1 created, 0 skipped
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
        Then import should succeed with 2 created, 0 skipped
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
        Then import should succeed with 2 created, 0 skipped
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


    Scenario: Import file fields can be in any order
        Given import file:
            language,translation,term,parent,status,tags,pronunciation
            Spanish,,gatos,gato,1,,
            Spanish,CAT,gato,,1,animal,GAH-toh
        Then import should succeed with 2 created, 0 skipped
        And words table should contain:
            gato
            gatos


    Scenario: Term can have multiple parents
        Given import file:
            language,translation,term,parent,status,tags,pronunciation
            Spanish,,gatos,"gato, cat",1,,
        Then import should succeed with 1 created, 0 skipped
        And words table should contain:
            cat
            gato
            gatos


    Scenario: Import file with only language and term
        Given import file:
            language,term
            Spanish,gato
            spanish,gatos
        Then import should succeed with 2 created, 0 skipped
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
