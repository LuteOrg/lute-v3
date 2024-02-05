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


    Scenario: Creating new multiword term when all are known
        Given language Spanish
        And text:
            Ella tiene una bebida.
        And all unknowns are set to known
        Then rendered should be:
            Ella(99)/ /tiene(99)/ /una(99)/ /bebida(99)/.
        Given terms:
            tiene UNA BEBIDA
        Then rendered should be:
            Ella(99)/ /tiene una bebida(1)/.


    # Prod bug: setting all to known in one Text wasn't updating another!
    Scenario: Marking words as known carries through to other texts
        Given language Spanish
        And text:
            Ella tiene una bebida.
        And all unknowns are set to known
        Then rendered should be:
            Ella(99)/ /tiene(99)/ /una(99)/ /bebida(99)/.
        Given text:
            Ella tiene un gato.
        Then rendered should be:
            Ella(99)/ /tiene(99)/ /un/ /gato/.


    # "Hasta cuando no juega, pero bueno." was getting rendered as
    # "Hasta cuando nono juega, pero bueno.", when all terms were
    # known, but "cuando no" was a mword term.
    Scenario: Fixed bug: "no" rendered correctly
        Given language Spanish
        And text:
            Hasta cuando no juega, pero bueno.
        And all unknowns are set to known
        Then rendered should be:
            Hasta(99)/ /cuando(99)/ /no(99)/ /juega(99)/, /pero(99)/ /bueno(99)/.
        Given term "hasta" with status 1
        And term "cuando no" with status 2
        Then rendered should be:
            Hasta(1)/ /cuando no(2)/ /juega(99)/, /pero(99)/ /bueno(99)/.


    Scenario: New term with new parent
        Given language Spanish
        And text:
            tiene y tener.
        And term "tiene" with status 1 and parent "tener"
        Then rendered should be:
            tiene(1)/ /y/ /tener(1)/.
        And words table should contain:
            tener
            tiene


    Scenario: New term with new parent, accented parent not updated
        Given language Spanish
        And text:
            Tengo que y qué.
        Then rendered should be:
            Tengo/ /que/ /y/ /qué/.
        Given term "tengo" with status 1 and parent "que"
        Then rendered should be:
            Tengo(1)/ /que(1)/ /y/ /qué/.


    Scenario: Multiword parent
        Given language Spanish
        And text:
            Hola tengo un gato.
        And term "tengo" with status 3 and parent "un gato"
        Then rendered should be:
            Hola/ /tengo(3)/ /un gato(3)/.


    Scenario: Fixed bug: change status of multiword term
        Given language Spanish
        And text:
            Hola tengo un gato.
        And term "un gato" with status 1
        Then rendered should be:
            Hola/ /tengo/ /un gato(1)/.
        Given term "un gato" with status 5
        Then rendered should be:
            Hola/ /tengo/ /un gato(5)/.


    Scenario: Fixed bug: doe with parent
        Given language Spanish
        And text:
            tiene y tener uno.
        And term "tiene" with status 1 and parent "tener uno"
        Then rendered should be:
            tiene(1)/ /y/ /tener uno(1)/.
        And words table should contain:
            tener/ /uno
            tiene


    # While using Lute v1, I ran into problems with specific sentences,
    # and fixed them.  Ported to v2, and now to v3.
    # Mis-spell of "to-do" is intentional :-P
    Scenario: Fixed bugs: production Spanish bugs
        Given language Spanish
        And text:
            ¿Qué me dice si nos acercamos al bar de la plaza de Sarriá y nos marcamos dos bocadillos de tortilla con muchísima cebolla?
            Un doctor de Cáceres le dijo una vez a mi madre que los Romero de Torres éramos el eslabón perdido entre el hombre y el pez martillo, porque el noventa por ciento de nuestro organismo es cartílago, mayormente concentrado en la nariz y en el pabellón auditivo.
            En la mesa contigua, un hombre observaba a Fermín de refilón por encima del periódico, probablemente pensando lo mismo que yo.
            Pese a toddo lo que pasó luego y a que nos distanciamos con el tiempo, fuimos buenos amigos:
            Tanto daba si había pasado el día trabajando en los campos o llevaba encima los mismos harapos de toda la semana.
        And terms:
            Un gato
            de refilón
            con el tiempo
            pabellón auditivo
            nos marcamos
            Tanto daba
        Then known-only rendered should be:
            ¿Qué me dice si nos acercamos al bar de la plaza de Sarriá y [[nos marcamos]] dos bocadillos de tortilla con muchísima cebolla?
            Un doctor de Cáceres le dijo una vez a mi madre que los Romero de Torres éramos el eslabón perdido entre el hombre y el pez martillo, porque el noventa por ciento de nuestro organismo es cartílago, mayormente concentrado en la nariz y en el [[pabellón auditivo]].
            En la mesa contigua, un hombre observaba a Fermín [[de refilón]] por encima del periódico, probablemente pensando lo mismo que yo.
            Pese a toddo lo que pasó luego y a que nos distanciamos [[con el tiempo]], fuimos buenos amigos:
            [[Tanto daba]] si había pasado el día trabajando en los campos o llevaba encima los mismos harapos de toda la semana.



    Scenario: Fixed bug: capitalized words are marked as known
        Given language Spanish
        And text:
            Á la una. Éste fué hallado. A la una.
        And all unknowns are set to known
        And all unknowns are set to known
        Then rendered should be:
            Á(99)/ /la(99)/ /una(99)/. /Éste(99)/ /fué(99)/ /hallado(99)/. /A(99)/ /la(99)/ /una(99)/.
        And words table should contain:
            a
            fué
            hallado
            la
            una
            á
            éste


    Scenario: Fixed bug: issue 10 multiwords are rendered in new texts
        Given language Spanish
        And terms:
            un gato
        And text:
            Tienes un gato.
        Then rendered should be:
            Tienes/ /un gato(1)/.
        Given text:
            Tengo un gato.
        Then rendered should be:
            Tengo/ /un gato(1)/.


    Scenario: Fixed bug: issue 10 multiwords with known in new text
        Given language English
        And terms:
            Associated Press
        And text:
            Abc wrote to the Associated Press about it.
        And all unknowns are set to known
        Then rendered should be:
            Abc(99)/ /wrote(99)/ /to(99)/ /the(99)/ /Associated Press(1)/ /about(99)/ /it(99)/.
        Given text:
            Def wrote to the Associated Press about it.
        Then rendered should be:
            Def/ /wrote(99)/ /to(99)/ /the(99)/ /Associated Press(1)/ /about(99)/ /it(99)/.
        Given text:
            Ghi wrote to the Associated Press about it.
        Then rendered should be:
            Ghi/ /wrote(99)/ /to(99)/ /the(99)/ /Associated Press(1)/ /about(99)/ /it(99)/.


    Scenario: Bulk updating terms
        Given language Spanish
        And terms:
            un gato
            lista
            tiene una
        And text:
            Hola tengo un gato.  No tengo una lista.
            Ella tiene una bebida.
        Then rendered should be:
            Hola/ /tengo/ /un gato(1)/. /No/ /tengo/ /una/ /lista(1)/.
            Ella/ /tiene una(1)/ /bebida/.
        Given bulk status 5 update for terms:
            tengo
            lista
            perro
        Then rendered should be:
            Hola/ /tengo(5)/ /un gato(1)/. /No/ /tengo(5)/ /una/ /lista(5)/.
            Ella/ /tiene una(1)/ /bebida/.


    Scenario: Turkish text
        Given language Turkish
        And text:
            ışık için Işık İçin.
        Then rendered should be:
            ışık/ /için/ /Işık/ /İçin/.
        Given term "ışık" with status 1
        Then rendered should be:
            ışık(1)/ /için/ /Işık(1)/ /İçin/.
        Given term "İçin" with status 3
        Then rendered should be:
            ışık(1)/ /için(3)/ /Işık(1)/ /İçin(3)/.



    Scenario: Japanese text.
        Given language Japanese
        And text:
            私は元気です.
        Then rendered should be:
            私/は/元気/です/.
        Given terms:
            私
            元気
            です
        Then rendered should be:
            私(1)/は/元気(1)/です(1)/.


    Scenario: Japanese multiword at end of sentence.
        Given language Japanese
        And text:
            2後ヲウメニ能問アラ費理セイ北多国び持困寿ながち。
        Then rendered should be:
            2/後/ヲ/ウメニ/能/問/アラ/費/理/セイ/北/多国/び/持/困/寿/な/がち/。
        Given terms:
            ながち
        Then rendered should be:
            2/後/ヲ/ウメニ/能/問/アラ/費/理/セイ/北/多国/び/持/困/寿/ながち(1)/。


    Scenario: Japanese multiword
        Given language Japanese
        And text:
            私は元気です.
        Then rendered should be:
            私/は/元気/です/.
        Given terms:
            元気です
        Then rendered should be:
            私/は/元気です(1)/.


    Scenario: Japanese multiword with numbers
        Given language Japanese
        And text:
            1234おれの方が強い。
        Then rendered should be:
            1234/おれ/の/方/が/強い/。
        Given terms:
            おれの方
        Then rendered should be:
            1234/おれの方(1)/が/強い/。


    Scenario: Bug fix: ru at end of sentence
        Given language Japanese
        And text:
            している
        And terms:
            している
        Then rendered should be:
            している(1)


    Scenario: Bug fix: classical chinese first character
        Given language Classical Chinese
        And text:
            關關。
        Then rendered should be:
            關/關/。
        Given terms:
            關
        Then rendered should be:
            關(1)/關(1)/。


# Template
    # Scenario: x
    #     Given language x
    #     And terms:
    #         x
    #     And text:
    #         x
    #     Then rendered should be:
    #         x
