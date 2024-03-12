Feature: Term import updating Status 0 terms
    If a term is in the database, but its status is 0, it is still "unknown" --
    it's a placeholder record only.  It's as if the term doesn't exist in the db.
    For that reason, it should only be created (set to different status)
    if the "create" is set to true.

    Background:
        Given demo data

    Scenario: Status 0 terms are updated if create true
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false, new as unknown true
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoTranslation, WoStatus from words order by WoText" should return:
            gato; cat; 0

        Given import file:
            language,term,translation,status
            Spanish,gato,kitty,1

        When import with create true, update false, new as unknown false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoTranslation, WoStatus from words order by WoText" should return:
            gato; kitty; 1


    Scenario: Status 0 terms are set to status 1 if created but status not set.
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false, new as unknown true
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoTranslation, WoStatus from words order by WoText" should return:
            gato; cat; 0

        Given import file:
            language,term,translation
            Spanish,gato,kitty
        When import with create true, update false, new as unknown false
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoTranslation, WoStatus from words order by WoText" should return:
            gato; kitty; 1


    Scenario: Status 0 terms not updated if create false
        Given import file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gato,cat,,1,"animal, noun",GA-toh
        When import with create true, update false, new as unknown true
        Then import should succeed with 1 created, 0 updated, 0 skipped
        And sql "select WoText, WoTranslation, WoStatus from words order by WoText" should return:
            gato; cat; 0

        Given import file:
            language,term,translation
            Spanish,gato,kitty
        When import with create false, update true, new as unknown false
        Then import should succeed with 0 created, 0 updated, 1 skipped
        And sql "select WoText, WoStatus from words order by WoText" should return:
            gato; 0
