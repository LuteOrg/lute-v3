# Antigravity Rules for Lute-v3 Development

## Environment & Permissions
1.  **Check Permissions First**: Lute v3 on macOS is prone to TCC (Transparency, Consent, and Control) issues. If you encounter `PermissionError` or `Operation not permitted`:
    -   Check if the terminal/editor has "Full Disk Access".
    -   Use the `sandbox-wrapper.sh` if available.
    -   Verify read access to `lute/config/config.yml` and write access to `data/*.db`.

## Testing Strategy
1.  **Prioritize Backend Unit Tests**: `pytest tests/unit/...` are reliable. Use them to verify logic changes (e.g., calculations, regex).
2.  **Verify Frontend Manually**: Frontend automation (`tests/acceptance/...`) is flaky due to `chromedriver` dependency. Use `browser_subagent` to verify critical UI interactions (clicking, saving) on a running server if automation fails.
3.  **Jinja Syntax**: When modifying complex Jinja2 templates (especially with embedded JavaScript), verify the syntax with a standalone script to ensure no auto-formatter mangled the code.

## Code Quality
1.  **Variable Injection**: Be extremely careful with Jinja variable injection into JavaScript (`{{ var | safe }}`).
2.  **Database**: Ensure the `demo_db.db` file is writable before assuming application logic errors. A read-only DB often manifests as misleading 500 errors or partial page loads.
