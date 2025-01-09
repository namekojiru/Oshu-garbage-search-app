import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
    }
    BABEL_DEFAULT_LOCALE = 'ja'
    BABEL_TRANSLATION_DIRECTORIES = './translations'