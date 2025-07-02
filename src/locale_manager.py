import json
import os

class LocaleManager:
    def __init__(self, language='ru'):
        self.language = language
        self.translations = self.load_translations()
    
    def load_translations(self):
        try:
            locale_path = os.path.join('locales', f'{self.language}.json')
            with open(locale_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            return {
                'app_title': "ntrp",
                'error_title': "Error",
                'export_error': "Export error"
            }
    
    def set_language(self, language):
        self.language = language
        self.translations = self.load_translations()
    
    def tr(self, key, **kwargs):
        translation = self.translations.get(key, key)
        if isinstance(translation, str):
            return translation.format(**kwargs) if kwargs else translation
        return key
    