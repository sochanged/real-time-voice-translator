"""
Application Configuration File.

This file stores configurations for the LinguaSync application,
such as supported languages and default settings.
"""

# Dictionary mapping human-readable language names to their API codes
# These codes are used by various translation and speech recognition services.
language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es",
    "Chinese (Simplified)": "zh-CN",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "German": "de",
    "French": "fr",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Gujarati": "gu",
    "Punjabi": "pa"
}

# Default language settings for the application.
# These can be used to set the initial state of the language selection comboboxes.
DEFAULT_INPUT_LANGUAGE_NAME = "English"  # Default input language name. Use "auto" for auto-detection if supported.
DEFAULT_OUTPUT_LANGUAGE_NAME = "Spanish" # Default output language name.

# Example on how to derive language codes from the names above:
# DEFAULT_INPUT_LANGUAGE_CODE = language_codes.get(DEFAULT_INPUT_LANGUAGE_NAME, "auto")
# DEFAULT_OUTPUT_LANGUAGE_CODE = language_codes.get(DEFAULT_OUTPUT_LANGUAGE_NAME, "en")

# Placeholder for API keys or other settings if the application is extended
# to use authenticated API access or has other configurable parameters.
# For example:
# GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
#
# Note: Currently, the application relies on default (often unauthenticated)
# access provided by the client libraries for Google services.
