Feature: Manage settings, backups

    Background:
        Given a running site
        And demo languages

    Scenario: I can list languages from the settings menu
        When I open the language index
        Then the page contains "Arabic"
        And the page contains "Classical Chinese"
        And the page contains "Czech"
        And the page contains "English"
        And the page contains "French"
        And the page contains "German"
        And the page contains "Greek"
        And the page contains "Hindi"
        And the page contains "Japanese"
        And the page contains "Russian"
        And the page contains "Sanskrit"
        And the page contains "Spanish"
        And the page contains "Turkish"

    Scenario: Backup settings use the expected defaults
        Then the backup settings are:
            backup_enabled: false
            backup_dir: default
            backup_auto: true
            backup_warn: true
            backup_count: 5
