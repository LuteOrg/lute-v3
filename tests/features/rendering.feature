Feature: Rendering
    Text is rendered correctly.

    Background:
        Given demo data


    Scenario: Smoke test
        Given language English
        And terms:
            lines
            and
        And text:
            Several lines of text,
            and also a blank line.
            
            And some more.
        Then rendered should be:
            Several/ /lines(1)/ /of/ /text/,
            and(1)/ /also/ /a/ /blank/ /line/.
            And(1)/ /some/ /more/.

    Scenario: No terms
        Given language Spanish
        And text:
            Hola tengo un gato.
        Then rendered should be:
            Hola/ /tengo/ /un/ /gato/.


    Scenario: Single term
        Given language Spanish
        And terms:
            tengo
        And text:
            Hola tengo un gato.
        Then rendered should be:
            Hola/ /tengo(1)/ /un/ /gato/.


    Scenario: Overlapping terms
        Given language Spanish
        And terms:
            tengo un
            un gato
        And text:
            Tengo un gato.
        Then rendered should be:
            Tengo un(1)/ gato(1)/.


    Scenario: Non overlapping terms
        Given language Spanish
        And terms:
            tengo un
            un gato
        And text:
            Tengo un un gato.
        Then rendered should be:
            Tengo un(1)/ /un gato(1)/.


    Scenario: Chain of overlapping terms
        Given language Spanish
        And terms:
            tengo un
            un gato
            gato bueno
        And text:
            Tengo un gato bueno.
        Then rendered should be:
            Tengo un(1)/ gato(1)/ bueno(1)/.


    Scenario: Chain of overlapping terms and one hidden
        Given language Spanish
        And terms:
            tengo un gato
            gato bueno
            un gato bueno y gordo
        And text:
            Tengo un gato bueno y gordo.
        Then rendered should be:
            Tengo un gato(1)/ bueno y gordo(1)/.


    Scenario: Text with numbers and quotes
        Given language Spanish
        And terms:
            tiene una bebida
        And text:
            121 111 123 "Ella tiene una bebida".
        Then rendered should be:
            121 111 123 "/Ella/ /tiene una bebida(1)/".


    Scenario: Term with numbers in the middle
        Given language Spanish
        And terms:
            tiene 1234 una bebida
        And text:
            Ella tiene 1234 una bebida.
        Then rendered should be:
            Ella/ /tiene 1234 una bebida(1)/.


    Scenario: Double spaces removed
        Given language Spanish
        And text:
            Hola  tengo     un gato.
        Then rendered should be:
            Hola/ /tengo/ /un/ /gato/.


    Scenario: Text contains same term many times.
        Given language Spanish
        And terms:
            UN GATO
        And text:
            Un gato es bueno. No hay un gato.  Veo a un gato.
        Then rendered should be:
            Un gato(1)/ /es/ /bueno/. /No/ /hay/ /un gato(1)/. /Veo/ /a/ /un gato(1)/.


    Scenario: Text same sentence contains same term many times.
        Given language Spanish
        And terms:
            UN GATO
        And text:
            Un gato es bueno, no hay un gato, veo a un gato.
        Then rendered should be:
            Un gato(1)/ /es/ /bueno/, /no/ /hay/ /un gato(1)/, /veo/ /a/ /un gato(1)/.


    Scenario: Apostrophes
        Given language English
        And terms:
            the cat's pyjamas
        And text:
            This is the cat's pyjamas.
        Then rendered should be:
            This/ /is/ /the cat's pyjamas(1)/.


    Scenario: No period at end of text
        Given language English
        And terms:
            word
        And text:
            Here is a word
        Then rendered should be:
            Here/ /is/ /a/ /word(1)


    Scenario: Capitals with accents
        Given language Spanish
        And terms:
            Á
        And text:
            Á la una. A la una, ábrelo á.
        Then rendered should be:
            Á(1)/ /la/ /una/. /A/ /la/ /una/, /ábrelo/ /á(1)/.


    Scenario: Marking words as known
        Given language Spanish
        And terms:
            lista
        And text:
            Tengo un GATO. Una lista.
            Ella.
        Then rendered should be:
            Tengo/ /un/ /GATO/. /Una/ /lista(1)/.
            Ella/.
        Given terms:
            TENGO
        Then rendered should be:
            Tengo(1)/ /un/ /GATO/. /Una/ /lista(1)/.
            Ella/.
        Given all unknowns are set to known
        Then rendered should be:
            Tengo(1)/ /un(99)/ /GATO(99)/. /Una(99)/ /lista(1)/.
            Ella(99)/.
        And words table should contain:
            ella
            gato
            lista
            tengo
            un
            una


# Template
    # Scenario: x
    #     Given language x
    #     And terms:
    #         x
    #     And text:
    #         x
    #     Then rendered should be:
    #         x
