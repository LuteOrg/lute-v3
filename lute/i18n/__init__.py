"""
Internationalisation module for Lute.
"""

from flask import session, request

try:
    from flask_babel import Babel
    HAS_BABEL = True
except ImportError:
    HAS_BABEL = False
    print("Warning: Flask-Babel not installed. Install with: pip install Flask-Babel>=4.0.0")

babel = None
if HAS_BABEL:
    babel = Babel()

def get_locale():
    """Determine the best language from the user's preferences."""
    # First check if user has set a language preference
    if 'language' in session:
        return session['language']
    
    # Try to guess the language from the user accept header
    return request.accept_languages.best_match(['es', 'fr', 'en']) or 'en'

def init_babel(app):
    """Initialize Babel with the Flask app."""
    # Configure languages even without Babel
    app.config['LANGUAGES'] = {
        'en': 'English',
        'es': 'Español', 
        'fr': 'Français'
    }
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    if HAS_BABEL and babel:
        babel.init_app(app, locale_selector=get_locale)
        return babel
    else:
        # Create a mock babel for development
        class MockBabel:
            def __init__(self):
                pass
        return MockBabel()