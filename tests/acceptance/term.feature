Feature: Creating and managing terms

    Background:
        Given a running site
        And demo languages
        Then the term table contains:
            No data available in table

    Scenario: Create a single term from the term form
        Given a new Spanish term:
            text: gato
            translation: cat
        Then the term table contains:
            ; gato; ; cat; Spanish; ; New (1)


    Scenario: Create a term and its parents at the same time
        Given a new Spanish term:
            text: aaaa
            parents: [ aa, bb ]
            translation: thing
        Then the term table contains:
            ; aa; ; thing; Spanish; ; New (1)
            ; aaaa; aa, bb; thing; Spanish; ; New (1)
            ; bb; ; thing; Spanish; ; New (1)


    Scenario: Import a valid term file
        Given import term file:
            language,term,translation,parent,status,tags,pronunciation
            Spanish,gatos,cat,gato,1,"animal, noun",GA-toh
        Then the term table contains:
            ; gato; ; cat; Spanish; animal, noun; New (1)
            ; gatos; gato; cat; Spanish; animal, noun; New (1)


    Scenario: Import Chinese terms
        Given import term file:
            language,term,translation,pronunciation,tags
            Classical Chinese,爱,love,ài,"HSK1"
            Classical Chinese,爱好,hobby,ài hào,"HSK1"
        Then the term table contains:
            ; 爱; ; love; Classical Chinese; HSK1; New (1)
            ; 爱好; ; hobby; Classical Chinese; HSK1; New (1)


# TODO testing scenarios: term filters.