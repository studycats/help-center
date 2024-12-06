import os, re
from deep_translator import GoogleTranslator

# languages = ['da', 'de', 'es', 'fi', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'no', 'pt', 'ru', 'sv', 'vi', 'zh-CN', 'zh-TW']
languages = ['zh-TW']
phrases = ['Learn English', 'Learn Spanish', 'Learn German', 'Learn Chinese', 'Learn French', 'Studycat']
replacements = ['[ENGL]','[ES]','[DTC]','[CH]', '[FRR]', '[STDCT]']

def substitution(text, list_originals, list_replacements):
    for i in range(len(list_originals)):
        replace = re.compile(re.escape(list_originals[i]), re.IGNORECASE)
        text = replace.sub(list_replacements[i], str(text))
    return text

def translate_markdown(text, target_language):
    if not text.strip():
        return text
        
    translator = GoogleTranslator(source='auto', target=target_language)
    
    # Store code blocks and their positions
    code_blocks = []
    pattern = r'```[\s\S]*?```|`[^`]+`'
    
    for match in re.finditer(pattern, text):
        code_blocks.append(match.group())

    # Replace code blocks with placeholders
    for i, block in enumerate(code_blocks):
        text = text.replace(block, f'[CODE_BLOCK_{i}]')

    # Substitute special phrases
    text = substitution(text, phrases, replacements)

    # Translate the text
    translated = translator.translate(text)

    # Restore special phrases
    translated = substitution(translated, replacements, phrases)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        translated = translated.replace(f'[CODE_BLOCK_{i}]', block)

    return translated

for language in languages:
    # Create language-specific directory if it doesn't exist
    target_dir = os.path.join('markdown', language)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Loop through files in markdown/en directory
    en_dir = os.path.join('markdown', 'en')

    # Check if directory exists
    if os.path.exists(en_dir):
        for filename in os.listdir(en_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(en_dir, filename)
                print(f"Processing {filename} for language {language}")

                try:
                    # Read source file
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()

                    # Translate content
                    translated_content = translate_markdown(content, language)

                    # Write translated content
                    with open(os.path.join(target_dir, filename), 'w', encoding='utf-8') as target_file:
                        target_file.write(translated_content)

                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    