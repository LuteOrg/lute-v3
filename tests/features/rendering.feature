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
