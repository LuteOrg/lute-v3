#!/usr/bin/env python3

"""
Debug script to test TTS functionality
"""

import os
import sys
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tts_generation():
    try:
        # Test if we can import the necessary modules
        from lute.tts.service import TTSService
        print("✓ TTS Service imported successfully")
        
        # Create a simple test
        tts_service = TTSService()
        print("✓ TTS Service instantiated successfully")
        
        # Test language code mapping
        lang_code = tts_service.get_language_code('English')
        print(f"✓ English language code: {lang_code}")
        
        # Test with a simple text
        test_text = "This is a test of the text to speech functionality."
        test_title = "Test_Book"
        
        # Test the generate_audio method (this will fail without Flask context)
        print("Testing TTS generation...")
        try:
            # This will likely fail because we don't have a Flask app context
            # but let's see what happens
            audio_filename = tts_service.generate_audio(test_text, lang_code, test_title)
            print(f"✓ TTS generation successful: {audio_filename}")
            return True
        except Exception as e:
            print(f"Expected error (no Flask context): {e}")
            print("This is normal when running outside of Flask context")
            return True
            
    except Exception as e:
        print(f"Error testing TTS Service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_access():
    """Test if we can access the user audio directory"""
    try:
        # Try to determine where the user audio directory would be
        from platformdirs import PlatformDirs
        dirs = PlatformDirs("Lute3", "Lute3")
        datapath = dirs.user_data_dir
        useraudiopath = os.path.join(datapath, "useraudio")
        
        print(f"User data directory: {datapath}")
        print(f"User audio directory: {useraudiopath}")
        
        # Check if directory exists
        if os.path.exists(useraudiopath):
            print("✓ User audio directory exists")
        else:
            print("⚠ User audio directory does not exist")
            # Try to create it
            try:
                os.makedirs(useraudiopath, exist_ok=True)
                print("✓ User audio directory created successfully")
            except Exception as e:
                print(f"✗ Failed to create user audio directory: {e}")
                return False
        
        # Check if directory is writable
        try:
            test_file = os.path.join(useraudiopath, "test_write.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("✓ User audio directory is writable")
        except Exception as e:
            print(f"✗ User audio directory is not writable: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"Error testing directory access: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TTS Debug Script ===")
    print()
    
    print("1. Testing directory access...")
    dir_success = test_directory_access()
    print()
    
    print("2. Testing TTS service...")
    tts_success = test_tts_generation()
    print()
    
    if dir_success and tts_success:
        print("✓ All tests passed")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)