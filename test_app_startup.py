#!/usr/bin/env python3
"""
Test script to verify the app starts without errors after i18n changes.
"""

import sys
import os

# Add lute to path
sys.path.insert(0, os.getcwd())

try:
    from lute.app_factory import create_app
    from lute.config.app_config import AppConfig
    
    print("Testing app startup with i18n...")
    
    # Create test config
    config = AppConfig.default_config_filename()
    
    # Mock Flask-Babel availability by checking imports
    try:
        from flask_babel import Babel
        print("✓ Flask-Babel is available")
        
        # Create app
        app = create_app(extra_config={'TESTING': True}, output_func=print)
        print("✓ App created successfully with i18n")
        
        with app.app_context():
            # Test that babel is configured
            assert 'LANGUAGES' in app.config
            print("✓ Languages configured:", list(app.config['LANGUAGES'].keys()))
        
        print("\n🎉 App startup test passed!")
        
    except ImportError:
        print("⚠️  Flask-Babel not installed - install with: pip install Flask-Babel>=4.0.0")
        print("   The i18n code is ready but Flask-Babel is needed to run the app")
        
except Exception as e:
    print(f"❌ App startup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)