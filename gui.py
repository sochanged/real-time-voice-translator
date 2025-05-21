"""
GUI module for the LinguaSync Real-Time Voice Translator.

This module defines the `Application` class, which encapsulates all the
graphical user interface elements and their interactions using Tkinter.
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
import logging

from app_config import language_codes

# Logger for this module
logger = logging.getLogger(__name__)

class Application:
    """
    The main GUI Application class for LinguaSync.

    This class is responsible for creating and managing all GUI widgets,
    handling user interactions, and interfacing with the TranslationService.
    """
    def __init__(self, master: tk.Tk):
        """
        Initializes the Application GUI.

        Args:
            master: The root Tkinter window.
        """
        self.master = master
        self.translator_service = None  # Will hold the TranslationService instance

        master.geometry("700x450")
        master.title("LinguaSync: Real-Time Voice🎙️ Translator🔊")
        
        logger.info("Initializing GUI components.")

        # Load and set application icon
        try:
            self.icon = tk.PhotoImage(file="icon.png")
            master.iconphoto(False, self.icon)
            logger.debug("Application icon loaded successfully.")
        except tk.TclError:
            logger.warning("Could not load icon.png. Make sure it's in the correct path.", exc_info=False) # No need for stack trace here
            self.icon = None

        # --- UI Elements Setup ---
        self._setup_text_areas()
        self._setup_language_selectors()
        self._setup_buttons()
        
        logger.info("GUI components initialized.")

    def _setup_text_areas(self):
        """Sets up the input and output text areas."""
        logger.debug("Setting up text areas.")
        self.input_label = tk.Label(self.master, text="Recognized Text ⮯")
        self.input_label.pack()
        self.input_text = tk.Text(self.master, height=5, width=50)
        self.input_text.pack()

        self.output_label = tk.Label(self.master, text="Translated Text ⮯")
        self.output_label.pack()
        self.output_text = tk.Text(self.master, height=5, width=50)
        self.output_text.pack()

        # Blank space for layout
        tk.Label(self.master, text="").pack()

    def _setup_language_selectors(self):
        """Sets up the language selection dropdown menus (Comboboxes)."""
        logger.debug("Setting up language selectors.")
        self.language_names = list(language_codes.keys())

        # Input language selector
        self.input_lang_label = tk.Label(self.master, text="Select Input Language:")
        self.input_lang_label.pack()
        self.input_lang_combobox = ttk.Combobox(self.master, values=self.language_names, state="readonly")
        self.input_lang_combobox.bind("<<ComboboxSelected>>", self._update_input_lang_code_event)
        default_input_name = "English" 
        self.input_lang_combobox.set(default_input_name if default_input_name in self.language_names else "auto")
        self.selected_input_lang_code = language_codes.get(self.input_lang_combobox.get(), "auto")
        logger.info(f"Default input language set to: {self.input_lang_combobox.get()} ({self.selected_input_lang_code})")
        self.input_lang_combobox.pack()

        # Visual separator
        tk.Label(self.master, text="▼").pack()

        # Output language selector
        self.output_lang_label = tk.Label(self.master, text="Select Output Language:")
        self.output_lang_label.pack()
        self.output_lang_combobox = ttk.Combobox(self.master, values=self.language_names, state="readonly")
        self.output_lang_combobox.bind("<<ComboboxSelected>>", self._update_output_lang_code_event)
        default_output_name = "Spanish"
        self.output_lang_combobox.set(default_output_name if default_output_name in self.language_names else (self.language_names[0] if self.language_names else ""))
        self.selected_output_lang_code = language_codes.get(self.output_lang_combobox.get(), "en")
        logger.info(f"Default output language set to: {self.output_lang_combobox.get()} ({self.selected_output_lang_code})")
        self.output_lang_combobox.pack()
        
        # Blank space for layout
        tk.Label(self.master, text="").pack()

    def _setup_buttons(self):
        """Sets up the main action buttons."""
        logger.debug("Setting up buttons.")
        self.run_button = tk.Button(self.master, text="Start Translation", command=self._start_translation_clicked_event)
        self.run_button.place(relx=0.25, rely=0.9, anchor="c")

        self.kill_button = tk.Button(self.master, text="Kill Execution", command=self._stop_translation_clicked_event)
        self.kill_button.place(relx=0.5, rely=0.9, anchor="c")

        self.about_button = tk.Button(self.master, text="About this project", command=self._open_about_page_event)
        self.about_button.place(relx=0.75, rely=0.9, anchor="c")

    def set_translation_service(self, service):
        """
        Sets the translation service instance for the GUI to use.

        Args:
            service: An instance of TranslationService.
        """
        self.translator_service = service
        logger.info("TranslationService instance linked to GUI.")

    def _start_translation_clicked_event(self):
        """Handles the 'Start Translation' button click event."""
        logger.info("'Start Translation' button clicked.")
        if self.translator_service:
            # Optionally clear previous text from display areas
            # self.input_text.delete('1.0', tk.END)
            # self.output_text.delete('1.0', tk.END)
            # logger.debug("Cleared input/output text areas.")
            self.translator_service.start_translation()
        else:
            err_msg = "Translation service not configured."
            logger.error(f"Cannot start translation: {err_msg}")
            self.show_error_message(err_msg)

    def _stop_translation_clicked_event(self):
        """Handles the 'Kill Execution' button click event."""
        logger.info("'Kill Execution' button clicked.")
        if self.translator_service:
            self.translator_service.stop_translation()
        else:
            err_msg = "Translation service not configured."
            logger.error(f"Cannot stop translation: {err_msg}")
            self.show_error_message(err_msg)

    def _update_input_lang_code_event(self, event):
        """
        Handles the input language selection event from the Combobox.
        Updates the internal state for the selected input language code.

        Args:
            event: The Tkinter event object (unused, but passed by the binding).
        """
        selected_language_name = self.input_lang_combobox.get()
        self.selected_input_lang_code = language_codes.get(selected_language_name, "auto")
        logger.info(f"Input language selection changed to: {selected_language_name} ({self.selected_input_lang_code})")

    def _update_output_lang_code_event(self, event):
        """
        Handles the output language selection event from the Combobox.
        Updates the internal state for the selected output language code.

        Args:
            event: The Tkinter event object (unused, but passed by the binding).
        """
        selected_language_name = self.output_lang_combobox.get()
        self.selected_output_lang_code = language_codes.get(selected_language_name, "en")
        logger.info(f"Output language selection changed to: {selected_language_name} ({self.selected_output_lang_code})")

    def _open_webpage_util(self, url: str):
        """
        Opens a web page in the user's default web browser.

        Args:
            url: The URL to open.
        """
        try:
            webbrowser.open(url)
            logger.info(f"Opened web page: {url}")
        except Exception as e:
            logger.error(f"Failed to open web page {url}: {e}", exc_info=True)
            self.show_error_message(f"Could not open web page: {url}")

    def _open_about_page_event(self):
        """Handles the 'About this project' button click event. Displays the About window."""
        logger.info("'About this project' button clicked.")
        about_window = tk.Toplevel(self.master)
        about_window.title("About LinguaSync")
        if self.icon: 
            about_window.iconphoto(False, self.icon)

        # GitHub link
        github_link = ttk.Label(about_window, text="github.com/SamirPaulb/real-time-voice-translator",
                                underline=True, foreground="blue", cursor="hand2")
        github_link.bind("<Button-1>", lambda e: self._open_webpage_util("https://github.com/SamirPaulb/real-time-voice-translator"))
        github_link.pack(pady=(10, 5)) # Added padding

        # About text
        about_text_content = """
LinguaSync: Real-Time Voice Translator

This application translates voice from one language to 
another in real-time, aiming to preserve the speaker's 
tone and emotion. It utilizes various Google services for 
its core translation functionalities.

Select input and output languages, then click 'Start Translation'.
Speak clearly into your microphone.
Say "exit" or "stop" to halt the current translation session.
"""
        about_text_widget = tk.Text(about_window, height=10, width=60, wrap=tk.WORD, relief=tk.FLAT, bg=about_window.cget('bg'))
        about_text_widget.insert("1.0", about_text_content.strip())
        about_text_widget.config(state=tk.DISABLED) 
        about_text_widget.pack(padx=10, pady=5)

        # Close button for the About window
        close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=(5, 10)) # Added padding
        
        # Modal behavior for the About window
        about_window.transient(self.master) 
        about_window.grab_set() 
        self.master.wait_window(about_window) # Wait until about_window is closed
        logger.debug("About window closed.")

    def show_error_message(self, message: str):
        """
        Displays an error message in the output_text widget of the GUI.

        Args:
            message: The error message string to display.
        """
        logger.error(f"Displaying error in GUI: {message}")
        if self.output_text:
            self.output_text.insert(tk.END, f"ERROR: {message}\n")
            self.output_text.see(tk.END) # Scroll to the end
        else:
            # Fallback if output_text is somehow not available
            logger.critical("output_text widget not available for error display.")
            print(f"GUI Error Display Attempt (output_text not available): {message}")

# Example of how to run this GUI module independently for testing (optional)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
    logger.info("Running gui.py directly for testing purposes.")
    root = tk.Tk()
    app = Application(root)
    
    # Example: Simulate TranslationService for testing button functionality
    class MockTranslationService:
        def start_translation(self): logger.info("MockService: Start translation called.")
        def stop_translation(self): logger.info("MockService: Stop translation called.")
    
    mock_service = MockTranslationService()
    app.set_translation_service(mock_service)
    
    # Example: Test show_error_message after a delay
    # root.after(2000, lambda: app.show_error_message("This is a test error message from __main__."))
    
    root.mainloop()
    logger.info("gui.py test run finished.")
