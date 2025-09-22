import os
import re
from flask import current_app
from gtts import gTTS

class TTSService:
    def get_language_code(self, language_name):
        """
        Get the gTTS language code for a given language name.
        
        Args:
            language_name (str): The name of the language (e.g., 'English', 'Spanish')
            
        Returns:
            str: The corresponding gTTS language code
        """
        # Mapping of language names to gTTS codes
        mapping = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Dutch': 'nl',
            'Russian': 'ru',
            'Japanese': 'ja',
            'Chinese': 'zh-CN',
            'Korean': 'ko',
            # Add more languages as needed
        }
        return mapping.get(language_name, 'en')  # Default to English if not found

    def generate_audio(self, text, language_code, book_title, progress_callback=None):
        """
        Generate an audio file from text using gTTS.
        
        Args:
            text (str): The text to convert to speech
            language_code (str): The language code (e.g., 'en', 'es', 'fr')
            book_title (str): The title of the book (used for filename)
            progress_callback (function): Optional callback function to report progress
            
        Returns:
            str: The path to the generated audio file
        """
        try:
            print(f"TTS Service: generate_audio called with language_code={language_code}, book_title={book_title}")
            print(f"TTS Service: text length={len(text) if text else 0}")
            
            # Report start of process
            if progress_callback:
                progress_callback(0, "Initializing TTS engine...")
            
            # Create a gTTS object
            print("TTS Service: Creating gTTS object")
            tts = gTTS(text=text, lang=language_code, slow=False, lang_check=False)
            
            # Report progress
            if progress_callback:
                progress_callback(30, "Generating audio...")
            
            # Generate a safe filename by sanitizing the book title
            # Remove or replace invalid characters for Windows file names
            safe_title = re.sub(r'[<>:"/\\|?*]', '', book_title.replace(' ', '_'))
            # Limit filename length to prevent issues
            if len(safe_title) > 100:
                safe_title = safe_title[:100]
            filename = f"{safe_title}_{hash(text) % 10000}.mp3"
            
            # Handle the case where we don't have a Flask app context
            try:
                filepath = os.path.join(current_app.env_config.useraudiopath, filename)
                print(f"TTS Service: Saving audio to {filepath}")
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
            except Exception as e:
                # Fallback to a default location if we can't access Flask context
                print(f"TTS Service: Flask context not available: {e}")
                # Try to create a useraudio directory in the current working directory
                useraudiopath = os.path.join(os.getcwd(), "useraudio")
                os.makedirs(useraudiopath, exist_ok=True)
                filepath = os.path.join(useraudiopath, filename)
                print(f"TTS Service: Using fallback path: {filepath}")
            
            # Report progress
            if progress_callback:
                progress_callback(60, "Saving audio file...")
            
            # Save the audio file
            tts.save(filepath)
            
            # Report completion
            if progress_callback:
                progress_callback(100, "Audio generation complete!")
            
            print(f"TTS Service: Audio generation complete, returning filename={filename}")
            return filename
        except Exception as e:
            print(f"TTS Service: Error during audio generation: {e}")
            import traceback
            traceback.print_exc()
            if progress_callback:
                progress_callback(-1, f"Error: {str(e)}")
            raise RuntimeError(f"Failed to generate TTS audio: {str(e)}") from e
