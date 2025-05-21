## Functional Map

This section provides a detailed functional map of the "LinguaSync: Real-Time Voice Translator" project, outlining its core functions, their interactions, typical user flow, and the external APIs utilized. The analysis is based on the `main.py` script and the `README.md` document.

### Core Functions and Descriptions

The application integrates several core functions to achieve its real-time voice translation capabilities:

1.  **GUI Interaction & Management (Tkinter):**
    *   **Description:** Provides the user interface for all operations. This includes displaying recognized and translated text, selecting input and output languages, starting/stopping the translation process, and accessing information about the application.
    *   **Key components in `main.py`:** Tkinter widget setup (`tk.Tk`, `tk.Label`, `tk.Text`, `ttk.Combobox`, `tk.Button`), event handlers (`run_translator`, `kill_execution`, `open_about_page`, language selection callbacks).

2.  **Voice Capture (SpeechRecognition & PyAudio):**
    *   **Description:** Actively listens to the microphone to capture the user's speech.
    *   **Key components in `main.py`:** `sr.Recognizer()`, `sr.Microphone()`, `r.listen(source)`.

3.  **Speech-to-Text Conversion (SpeechRecognition library):**
    *   **Description:** Converts the captured audio data into editable text.
    *   **Key components in `main.py`:** `r.recognize_google(audio)`.

4.  **Transliteration (google-transliteration-api library):**
    *   **Description:** (Optional) Converts the script of the recognized text from one writing system to another, if the input language is not English or 'auto'. This can be useful for languages that have common phonetic spellings in Roman characters but use a different native script.
    *   **Key components in `main.py`:** `transliterate_text(speech_text, lang_code=input_lang.get())`.

5.  **Text-to-Text Translation (deep-translator library):**
    *   **Description:** Translates the (potentially transliterated) text from the source language to the target language.
    *   **Key components in `main.py`:** `GoogleTranslator(source=input_lang.get(), target=output_lang.get()).translate(text=...)`.

6.  **Text-to-Speech Synthesis (gTTS library):**
    *   **Description:** Converts the translated text back into audible speech in the target language.
    *   **Key components in `main.py`:** `gTTS(translated_text, lang=output_lang.get())`, `voice.save('voice.mp3')`.

7.  **Audio Playback (playsound library):**
    *   **Description:** Plays the generated speech audio file.
    *   **Key components in `main.py`:** `playsound('voice.mp3')`, followed by `os.remove('voice.mp3')`.

8.  **State Management & Orchestration:**
    *   **Description:** Controls the flow of the application, particularly the start and stop of the real-time translation loop, and manages data between the different functional components.
    *   **Key components in `main.py`:** `keep_running` global variable, `update_translation()` function acting as the main loop, `run_translator()` starting the loop in a thread, `kill_execution()` stopping it.

### Functional Interactions and Flow

The core functions interact in a sequential pipeline, orchestrated by the `update_translation()` function, which runs in a loop when active. The `README.md` provides a block diagram illustrating this flow.

**Textual Representation of the Main Translation Flow (within `update_translation()` loop):**

```
User Speaks
    └──> 1. Voice Capture (Microphone via SpeechRecognition)
        └──> Raw Audio Data
            └──> 2. Speech-to-Text (SpeechRecognition -> Google Web Speech API)
                └──> Recognized Text (e.g., "Hello")
                    │   └──> Display in "Recognized Text" GUI area
                    │
                    └──> (Optional) 3. Transliteration (if input lang not 'en'/'auto' via google-transliteration-api)
                        └──> Transliterated Text (e.g., if input was Hindi typed in Roman, converted to Devanagari)
                            └──> 4. Text-to-Text Translation (deep-translator -> Google Translate API)
                                └──> Translated Text (e.g., "Hola")
                                    │   └──> Display in "Translated Text" GUI area
                                    │
                                    └──> 5. Text-to-Speech (gTTS -> Google TTS API)
                                        └──> Audio Data (e.g., an MP3 of "Hola")
                                            └──> 6. Audio Playback (playsound)
                                                └──> User Hears Translated Speech
```

**Interaction Points:**
-   **GUI -> Orchestration:** User clicks "Start Translation" (`run_translator()`) or "Kill Execution" (`kill_execution()`). User selects languages from dropdowns, triggering `update_input_lang_code()` or `update_output_lang_code()`.
-   **Orchestration (`update_translation`) -> Core Functions:** Sequentially calls functions for voice capture, STT, transliteration, translation, TTS, and playback.
-   **Core Functions -> GUI:** Recognized and translated texts are inserted into their respective text areas. Error messages can also be displayed.

### Typical User Flow

1.  **Application Launch:** The user runs the application (`python main.py` or the executable). The main GUI window appears.
2.  **Language Selection (Optional):**
    *   The user selects their desired input language from the "Select Input Language" dropdown. Defaults to "auto".
    *   The user selects their desired output language from the "Select Output Language" dropdown. Defaults to "en" (English).
3.  **Start Translation:** The user clicks the "Start Translation" button.
    *   This triggers `run_translator()`, which sets `keep_running = True` and starts the `update_translation()` loop in a separate thread.
4.  **Speak:** The application prints "Speak Now!" to the console. The user speaks into their microphone.
5.  **Real-Time Processing:**
    *   The application captures the voice.
    *   Converts speech to text.
    *   Displays the recognized text in the "Recognized Text" box.
    *   (If applicable) Transliterates the text.
    *   Translates the text to the target language.
    *   Displays the translated text in the "Translated Text" box.
    *   Converts the translated text to speech.
    *   Plays the translated speech.
6.  **Continuous Translation:** Steps 4 and 5 repeat as long as `keep_running` is true, allowing for continuous conversation translation.
7.  **Stop Translation:**
    *   The user can say "exit" or "stop" (this is checked in `update_translation()`).
    *   Alternatively, the user can click the "Kill Execution" button.
    *   This sets `keep_running = False`, and the `update_translation()` loop terminates.
8.  **View About Page (Optional):** The user can click the "About this project" button to view more information and a link to the GitHub repository.
9.  **Close Application:** The user closes the Tkinter window.

### API Usage Analysis

The project relies on several external services through the Python libraries it uses:

1.  **SpeechRecognition library (`speech_recognition`):**
    *   The function `r.recognize_google(audio)` is used.
    *   **External API:** This function sends audio data to the **Google Web Speech API** for speech-to-text conversion. This is an online service and requires an internet connection.

2.  **deep-translator library (`deep_translator`):**
    *   The class `GoogleTranslator` is used (e.g., `GoogleTranslator(source=..., target=...).translate(text=...)`).
    *   **External API:** This library acts as a wrapper and sends text to the **Google Translate API** for translation. This is an online service and requires an internet connection.

3.  **gTTS library (`gtts`):**
    *   The class `gTTS(text=..., lang=...)` is used.
    *   **External API:** This library sends text to an undocumented **Google Text-to-Speech API** (often the same one that powers the "translate.google.com" read-aloud feature) to generate speech audio. This is an online service and requires an internet connection.

4.  **google-transliteration-api library (`google.transliteration`):**
    *   The function `transliterate_text(text=..., lang_code=...)` is used.
    *   **External API:** This library likely interacts with a **Google Input Tools API** or a similar service for transliteration. This is an online service and requires an internet connection.

**Summary of External Dependencies:**
The core functionality of LinguaSync (speech recognition, translation, TTS, and transliteration) is heavily dependent on Google's online services. If these services are unavailable (e.g., due to network issues, API changes, or rate limiting), the respective functionalities of the application will fail. The `README.md` mentions dependencies but doesn't explicitly highlight this reliance on external Google APIs for core operations, which is a crucial aspect of its functional architecture. The error handling in `main.py` for `sr.RequestError` ("Could not request from Google!") acknowledges this dependency to some extent for the speech recognition part.
