"""
Translation Service Module for LinguaSync.

This module defines the `TranslationService` class, which encapsulates
all the logic related to the voice translation pipeline, including
speech recognition, transliteration, text translation, and text-to-speech
synthesis and playback.
"""
import os
import threading
import tkinter as tk # For tk.END, consider removing if not essential for logic
import speech_recognition as sr
from playsound import playsound
from deep_translator import GoogleTranslator, exceptions as dt_exceptions
from gtts import gTTS, gTTSError
from google.transliteration import transliterate_text
import tempfile
import logging

# Logger for this module
logger = logging.getLogger(__name__)

class TranslationService:
    """
    Manages the core translation pipeline of the LinguaSync application.

    This service handles speech recognition, optional transliteration,
    text translation, text-to-speech synthesis, and audio playback.
    It runs the main translation loop in a separate thread to keep the
    GUI responsive and communicates with the GUI to display results and errors.
    """
    def __init__(self, app_instance):
        """
        Initializes the TranslationService.

        Args:
            app_instance: An instance of the `gui.Application` class, used for
                          interacting with the GUI (e.g., displaying text, errors).
        """
        self.app = app_instance
        self.keep_running = False
        self.update_thread = None
        self.recognizer = sr.Recognizer()
        logger.info("TranslationService initialized.")
        # Optional: Adjust recognizer for ambient noise once upon initialization.
        # This can improve recognition accuracy in noisy environments.
        # try:
        #     with sr.Microphone() as source:
        #         logger.debug("Adjusting for ambient noise... Please wait.")
        #         self.recognizer.adjust_for_ambient_noise(source, duration=1)
        #         logger.info("Recognizer adjusted for ambient noise.")
        # except Exception as e:
        #     logger.warning(f"Could not adjust for ambient noise: {e}", exc_info=False)

    def _recognize_speech_from_mic(self, source_audio: sr.AudioSource) -> tuple[str | None, str | None]:
        """
        Recognizes speech from the given audio source using Google Web Speech API.

        Args:
            source_audio: The `speech_recognition.AudioSource` to listen to.

        Returns:
            A tuple (recognized_text, None) on successful recognition,
            or (None, error_message_string) if recognition fails or an error occurs.
        """
        try:
            input_lang_code = self.app.selected_input_lang_code
            # Use None for language if 'auto' to let Google auto-detect
            language_param = input_lang_code if input_lang_code != "auto" else None
            
            logger.debug(f"Listening for speech via microphone... Language: {language_param or 'auto'}")
            audio = self.recognizer.listen(source_audio) 
            logger.debug("Processing captured speech...")
            speech_text = self.recognizer.recognize_google(audio, language=language_param)
            logger.info(f"Speech recognized: '{speech_text}'")
            return speech_text, None
        except sr.WaitTimeoutError:
            logger.warning("No speech detected within timeout.")
            return None, "No speech detected within timeout."
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio.")
            return None, "Could not understand audio."
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}", exc_info=True)
            return None, f"Speech API request failed: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during speech recognition: {e}", exc_info=True)
            return None, f"Speech recognition error: {type(e).__name__}"

    def _transliterate_if_needed(self, text: str, lang_code: str) -> tuple[str, str | None]:
        """
        Transliterates text if the language code is not English or 'auto'.

        Args:
            text: The text to transliterate.
            lang_code: The language code of the input text.

        Returns:
            A tuple (processed_text, None). `processed_text` is the transliterated
            text if transliteration occurred, otherwise it's the original text.
            If transliteration fails, returns (original_text, error_message_string).
        """
        if lang_code not in ('auto', 'en') and text: # Ensure text is not None or empty
            logger.debug(f"Attempting transliteration for language '{lang_code}' with text: '{text}'")
            try:
                transliterated_text = transliterate_text(text, lang_code=lang_code)
                logger.info(f"Text transliterated to '{lang_code}': '{transliterated_text}'")
                return transliterated_text, None
            except Exception as e:
                logger.error(f"Transliteration error for text '{text}' to lang_code '{lang_code}': {e}", exc_info=True)
                return text, f"Transliteration failed: {type(e).__name__}" 
        logger.debug(f"No transliteration needed for lang_code '{lang_code}' or empty text.")
        return text, None

    def _translate_text_content(self, text: str, source_lang: str, target_lang: str) -> tuple[str | None, str | None]:
        """
        Translates text using GoogleTranslator from the deep-translator library.

        Args:
            text: The text to translate.
            source_lang: The source language code.
            target_lang: The target language code.

        Returns:
            A tuple (translated_text, None) on success,
            or (None, error_message_string) if translation fails.
        """
        if not text: 
            logger.warning("No text provided for translation.")
            return None, "No text provided for translation."
        
        logger.debug(f"Attempting translation from '{source_lang}' to '{target_lang}' for text: '{text}'")
        try:
            translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text=text)
            logger.info(f"Text translated to '{target_lang}': '{translated_text}'")
            return translated_text, None
        except dt_exceptions.TranslationNotFound as e:
            logger.warning(f"Translation not found for text '{text}': {e}", exc_info=False) # Stack trace might be too verbose for this
            return None, f"Translation not found: Query '{text[:20]}...'" # Avoid overly long error messages
        except dt_exceptions.DeepTranslatorException as e: 
            logger.error(f"Translation API error: {e}", exc_info=True)
            return None, f"Translation API error: {type(e).__name__}"
        except Exception as e: 
            logger.error(f"Unexpected error during translation: {e}", exc_info=True)
            return None, f"Unexpected translation error: {type(e).__name__}"

    def _synthesize_and_play_audio(self, text: str, lang_code: str) -> tuple[bool, str | None]:
        """
        Synthesizes text to speech, plays it, and cleans up the temporary audio file.

        Args:
            text: The text to synthesize.
            lang_code: The language code for TTS.

        Returns:
            A tuple (True, None) on successful synthesis and playback,
            or (False, error_message_string) if any step fails.
        """
        if not text:
            logger.warning("No text provided for audio synthesis.")
            return False, "No text provided for synthesis."
        
        temp_audio_file_path = None
        try:
            # Create a named temporary file for the audio output.
            # delete=False is necessary because playsound needs to open the file by its path after gTTS saves to it.
            # We manually delete the file in the finally block.
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                temp_audio_file_path = tmp_file.name
            logger.debug(f"Created temporary audio file: {temp_audio_file_path}")
            
            # Synthesize speech using gTTS
            logger.debug(f"Synthesizing audio for text: '{text}' in language '{lang_code}'")
            voice = gTTS(text=text, lang=lang_code)
            voice.save(temp_audio_file_path)
            logger.info(f"Audio synthesized and saved to {temp_audio_file_path}")

            # Play the synthesized audio
            logger.debug(f"Playing audio file: {temp_audio_file_path}")
            playsound(temp_audio_file_path) 
            logger.info("Audio playback finished.")
            return True, None
        except gTTSError as e:
            logger.error(f"gTTS Error during synthesis for text '{text}': {e}", exc_info=True)
            return False, f"Text-to-Speech (gTTS) Error: {e}"
        except Exception as e: 
            logger.error(f"Audio synthesis or playback error for text '{text}': {e}", exc_info=True)
            return False, f"Audio synthesis/playback error: {type(e).__name__}"
        finally:
            # Ensure the temporary file is deleted if it was created
            if temp_audio_file_path and os.path.exists(temp_audio_file_path):
                try:
                    os.remove(temp_audio_file_path)
                    logger.debug(f"Temporary audio file {temp_audio_file_path} deleted successfully.")
                except OSError as e:
                    logger.error(f"Error deleting temporary audio file {temp_audio_file_path}: {e}", exc_info=True)

    def _update_translation_loop(self):
        """
        The main loop for the translation process, running in a separate thread.

        This loop continuously:
        1. Listens for speech via the microphone.
        2. Recognizes the speech to text.
        3. (Optionally) Transliterates the recognized text.
        4. Translates the text to the target language.
        5. Synthesizes the translated text to speech and plays it.
        6. Displays recognized text, translated text, and errors in the GUI.
        The loop continues as long as `self.keep_running` is True.
        """
        logger.debug(f"Translation loop iteration started. keep_running: {self.keep_running}")
        # Initial check to ensure loop should run and GUI is available
        if not (self.keep_running and self.app and hasattr(self.app, 'master') and self.app.master):
            if not self.keep_running: logger.info("Translation loop stopping: keep_running is false.")
            else: logger.warning("Translation loop stopping: GUI app or master window not available.")
            return

        try:
            with sr.Microphone() as source: # Using context manager for microphone
                # Optional: Adjust for ambient noise dynamically if issues persist,
                # but could also be done once in __init__.
                # logger.debug("Adjusting for ambient noise for current listening session...")
                # self.recognizer.adjust_for_ambient_noise(source, duration=0.2) 
                
                logger.info("Listening for user speech...")
                speech_text, error_msg = self._recognize_speech_from_mic(source)
                
                if error_msg: 
                    logger.warning(f"Speech recognition failed: {error_msg}")
                    self.app.show_error_message(f"Recognition: {error_msg}")
                    # Continue to allow next attempt without manual restart if keep_running is true
                    if self.keep_running: self.app.master.after(100, self._update_translation_loop)
                    return 
                
                # If speech_text is None but no error_msg (shouldn't happen with current helpers, but safeguard)
                if not speech_text: 
                    logger.debug("No speech text recognized, continuing loop.")
                    if self.keep_running: self.app.master.after(100, self._update_translation_loop)
                    return

                # Update GUI with recognized text
                self.app.input_text.insert(tk.END, f"{speech_text}\n") 
                self.app.input_text.see(tk.END) # Auto-scroll

                # Check for voice commands to stop translation
                if speech_text.lower() in {'exit', 'stop'}:
                    self.keep_running = False # Signal loop to stop
                    logger.info(f"Voice command '{speech_text}' received. Stopping translation.")
                    self.app.show_error_message("Translation stopped by voice command.")
                    return # Exit loop immediately

                # Proceed with transliteration and translation pipeline
                input_lang_code = self.app.selected_input_lang_code
                output_lang_code = self.app.selected_output_lang_code
                
                processed_text, error_msg = self._transliterate_if_needed(speech_text, input_lang_code)
                if error_msg: 
                    logger.warning(f"Transliteration failed: {error_msg}. Using original text for translation.")
                    self.app.show_error_message(f"Transliteration: {error_msg}")
                    # Continue with original text (processed_text holds original if translit failed)

                translated_text, error_msg = self._translate_text_content(processed_text, input_lang_code, output_lang_code)
                if error_msg: 
                    logger.error(f"Text translation failed: {error_msg}")
                    self.app.show_error_message(f"Translation: {error_msg}")
                    if self.keep_running: self.app.master.after(100, self._update_translation_loop)
                    return 
                
                if not translated_text: # Safeguard if translation returns None without specific error_msg
                    logger.warning("Translation resulted in empty text, not proceeding with audio.")
                    self.app.show_error_message("Translation resulted in empty text.")
                    if self.keep_running: self.app.master.after(100, self._update_translation_loop)
                    return
                
                # Update GUI with translated text
                self.app.output_text.insert(tk.END, translated_text + "\n")
                self.app.output_text.see(tk.END) # Auto-scroll

                # Synthesize and play audio
                _played_successfully, error_msg = self._synthesize_and_play_audio(translated_text, output_lang_code)
                if error_msg: 
                    logger.error(f"Audio synthesis or playback failed: {error_msg}")
                    self.app.show_error_message(f"Audio: {error_msg}")
        
        except sr.RequestError as e: # Specific error if microphone/speech API is initially unavailable
            logger.critical(f"Microphone or Speech API is unavailable: {e}", exc_info=True)
            self.app.show_error_message(f"Mic/Speech API unavailable: {e}")
            self.keep_running = False # Stop the loop if fundamental services are down
        except Exception as e: # Catch-all for unexpected errors in the loop's structure or sr.Microphone()
            logger.critical(f"Unexpected critical error in translation cycle: {e}", exc_info=True)
            self.app.show_error_message(f"Unexpected error in translation cycle: {type(e).__name__}")
            self.keep_running = False # Stop the loop on major unexpected errors

        # Schedule next iteration or stop
        if self.keep_running:
            logger.debug("Scheduling next iteration of translation loop.")
            self.app.master.after(100, self._update_translation_loop)
        else:
            logger.info("Translation loop has finished or been signaled to stop.")


    def start_translation(self):
        """Starts the real-time translation process in a separate thread."""
        if not self.keep_running:
            self.keep_running = True
            logger.info("Translation process started by user.")
            
            # Optionally clear previous text in GUI when starting a new session
            # self.app.input_text.delete('1.0', tk.END)
            # self.app.output_text.delete('1.0', tk.END)
            # logger.debug("Cleared input/output text areas on start.")
            
            # Ensure only one update thread is running
            if self.update_thread is None or not self.update_thread.is_alive():
                logger.debug("Creating and starting new translation thread.")
                self.update_thread = threading.Thread(target=self._update_translation_loop)
                self.update_thread.daemon = True # Ensures thread exits when main program exits
                self.update_thread.start()
            else:
                # This case should ideally not be reached if UI buttons are disabled appropriately
                logger.warning("Attempted to start translation thread, but it seems one is already running.")
        else:
            # This case should ideally not be reached if UI buttons are disabled appropriately
            logger.warning("Start translation called, but translation is already running.")


    def stop_translation(self):
        """Stops the real-time translation process."""
        if self.keep_running:
            self.keep_running = False # Signal the loop to stop
            logger.info("Translation process stopping initiated by user.")
            # The loop will check self.keep_running and exit.
            # Optional: Add logic to disable/enable buttons in GUI via self.app
            # self.app.run_button.config(state=tk.NORMAL)
            # self.app.kill_button.config(state=tk.DISABLED)
        else:
            logger.info("Stop translation called, but translation was not running or already stopping.")
