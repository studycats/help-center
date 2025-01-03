import os, re, configparser
from deep_translator import GoogleTranslator

# Initialize translator
translator = GoogleTranslator()

# List of target languages
languages = ['da', 'de', 'es', 'fi', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'no', 'pt', 'ru', 'sv', 'vi', 'zh-CN', 'zh-TW']
phrases = ['Learn English', 'Learn Spanish', 'Learn German', 'Learn Chinese', 'Learn French', 'Studycat']
replacements = ['[ENGL]','[ES]','[DTC]','[CH]', '[FRR]', '[STDCT]']

def substitution(text, list_originals, list_replacements):
    for i in range(len(list_originals)):
        replace = re.compile(re.escape(list_originals[i]), re.IGNORECASE)
        text = replace.sub(list_replacements[i], str(text))
    return text

def translate(level, language):
    config = configparser.ConfigParser()

    config.read(os.path.join(level, f'{level}_en.ini'))

    for section in config.sections():
        for key in config[section]:
            original_text = config[section][key]
            # Apply substitutions before translation
            text_with_replacements = substitution(original_text, phrases, replacements)
            # Translate the text
            translated_text = GoogleTranslator(source='auto', target=language).translate(text_with_replacements)
            # Apply substitutions again after translation in case Google translated our keywords
            translated_text = substitution(translated_text, replacements, phrases)
            config[section][key] = translated_text
    
    with open(os.path.join(level, f'{level}_{language}.ini'), 'w', encoding='utf-8') as f:
        config.write(f)

# Process each language
for language in languages:    
    translate('categories', language)
    translate('sections', language)
    
    print(f"Created translations for {language}")
