"""
LinguaSync - Real-Time Voice Translator Application.

This is the main entry point for the LinguaSync application.
It initializes the GUI, the translation service, and starts the Tkinter event loop.
"""
import tkinter as tk
import logging # Import the logging module

from gui import Application 
from translation_service import TranslationService

def main():
    """
    Initializes and runs the LinguaSync application.

    This function sets up the basic logging configuration, creates the main application
    window, instantiates the GUI Application class and the TranslationService class,
    links them, and then starts the Tkinter main event loop.
    """
    # Configure basic logging
    # This will log to both a file "app.log" and the console (StreamHandler)
    # It includes timestamp, log level, module name, and the log message.
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level (e.g., INFO, DEBUG)
        format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", mode='w'),  # Log to a file, overwrite each time
            logging.StreamHandler()  # Log to the console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Application starting...")

    win = tk.Tk()  # Create the main Tkinter window
    app_instance = Application(win)  # Create an instance of the GUI Application
    
    # Create an instance of the TranslationService, passing the GUI instance
    translator_service = TranslationService(app_instance) 
    
    # Link the translation service to the GUI application instance
    app_instance.set_translation_service(translator_service) 
    
    logger.info("Application GUI and TranslationService initialized. Starting main loop.")
    win.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    # This block executes when the script is run directly.
    main()
