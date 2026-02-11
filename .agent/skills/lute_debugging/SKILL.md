
---
name: verify_lute_env
description: Diagnose common Lute v3 development issues
---

# Verify Lute Environment Skill

This skill provides tools and scripts to quickly diagnose environment issues that often block Lute development, such as permission errors, missing dependencies, or database locks.

## Artifacts

- **verify_env.py**: A Python script to check:
    -   Readability of `lute/config/config.yml`.
    -   Writeability of `data/demo_db.db` (or configured DB).
    -   Jinja2 template syntax correctness.
    -   Python version and dependencies.

## Usage

1.  Run the verification script:
    ```bash
    python .agent/skills/lute_debugging/verify_env.py
    ```
2.  Check the output for `FAIL` or `WARN` messages.
3.  Fix reported permission issues (often solved by valid Full Disk Access on macOS).

## Common Issues

-   **PermissionError**: Usually TCC blocking access to `config.yml` or `data` folder on macOS.
-   **TemplateSyntaxError**: Often caused by auto-formatters breaking Jinja tags in JS blocks or incorrect context.
-   **SessionNotCreatedException**: Missing or incompatible `chromedriver` for acceptance tests.
