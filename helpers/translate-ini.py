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

# Process each language
for language in languages:
    # Initialize ConfigParser for reading INI files
    categories_config = configparser.ConfigParser()
    sections_config = configparser.ConfigParser()
    
    # Read original INI files
    categories_config.read(os.path.join('categories', 'categories_en.ini'))
    sections_config.read(os.path.join('sections', 'sections_en.ini'))
    
    # Translate categories
    for section in categories_config.sections():
        for key in categories_config[section]:
            original_text = categories_config[section][key]
            # Apply substitutions before translation
            text_with_replacements = substitution(original_text, phrases, replacements)
            # Translate the text
            translated_text = GoogleTranslator(source='auto', target=language).translate(text_with_replacements)
            # Apply substitutions again after translation in case Google translated our keywords
            translated_text = substitution(translated_text, replacements, phrases)
            categories_config[section][key] = translated_text
    
    # Translate sections
    for section in sections_config.sections():
        for key in sections_config[section]:
            original_text = sections_config[section][key]
            # Apply substitutions before translation
            text_with_replacements = substitution(original_text, phrases, replacements)
            # Translate the text
            translated_text = GoogleTranslator(source='auto', target=language).translate(text_with_replacements)
            # Apply substitutions again after translation in case Google translated our keywords
            translated_text = substitution(translated_text, replacements, phrases)
            sections_config[section][key] = translated_text
    
    # Save translated files with language code
    with open(os.path.join('categories', f'categories_{language}.ini'), 'w', encoding='utf-8') as f:
        categories_config.write(f)
    
    with open(os.path.join('sections', f'sections_{language}.ini'), 'w', encoding='utf-8') as f:
        sections_config.write(f)
    
    print(f"Created translations for {language}")
