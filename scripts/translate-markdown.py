import os, re, anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=api_key)
prompt = open('prompts/prompt.txt', 'r').read()
proofread = open('prompts/proofread.txt', 'r').read()

languages = {
    'da': 'Danish',
    'de': 'German',
    'es': 'Spanish',
    'fi': 'Finnish', 
    'fr': 'French',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ms': 'Malay',
    'no': 'Norwegian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sv': 'Swedish',
    'vi': 'Vietnamese',
    'zh-CN': 'Simplified Chinese',
    'zh-TW': 'Traditional Chinese'
}

phrases = ['Learn English', 'Learn Spanish', 'Learn German', 'Learn Chinese', 'Learn French', 'Studycat']
replacements = ['[ENGL]','[ES]','[DTC]','[CH]', '[FRR]', '[STDCT]']

def substitution(text, list_originals, list_replacements):
    for i in range(len(list_originals)):
        replace = re.compile(re.escape(list_originals[i]))
        text = replace.sub(list_replacements[i], str(text))
    return text

def call_claude(prompt, text, language, action):
    text = prompt.replace('[language]', language).replace('[markdown]', text)
    text += '\n[EOF]'

    return client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2048,
        system="You are a translator and proofreader, you only return the given Markdown in it's complete form.",
        messages=[
            {"role": "user", "content": text},
            {"role": "assistant", "content": f"Here is the {action} Markdown in full:" }
        ],
        stop_sequences=['[EOF]']
    ).content[0].text

def translate_markdown(text, target_language):
    if not text.strip():
        return text

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

    text = call_claude(prompt, text, languages[target_language], 'translated')

    text = call_claude(proofread, text, languages[target_language], 'proofread')

    # Restore special phrases
    text = substitution(text, replacements, phrases)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        text = text.replace(f'[CODE_BLOCK_{i}]', block)

    return text

for language in languages:
    # Create language-specific directory if it doesn't exist
    target_dir = os.path.join('markdown', language)
    os.makedirs(target_dir, exist_ok=True)

    source_dir = os.path.join('markdown', 'en')

    # Check if directory exists
    if os.path.exists(source_dir):
        for category in os.listdir(source_dir):
            source_category_folder = os.path.join(source_dir, category)
            target_category_folder = os.path.join(target_dir, category)
            os.makedirs(target_category_folder, exist_ok=True)

            for section in os.listdir(source_category_folder):
                source_section_folder = os.path.join(source_category_folder, section)
                target_section_folder = os.path.join(target_category_folder, section)
                os.makedirs(target_section_folder, exist_ok=True)

                for filename in os.listdir(source_section_folder):
                    if filename.endswith('.md') and not os.path.exists(os.path.join(target_section_folder, filename)):
                        file_path = os.path.join(source_section_folder, filename)
                        print(f"Processing {filename} for language {language}")

                        try:
                            # Read source file
                            with open(file_path, 'r', encoding='utf-8') as source_file:
                                content = source_file.read()

                            # Translate content
                            translated_content = translate_markdown(content, language)

                            # Remove content before first '---'
                            if '---' in translated_content:
                                translated_content = '---' + translated_content.split('---', 1)[1]

                            # Write translated content
                            with open(os.path.join(target_section_folder, filename), 'w', encoding='utf-8') as target_file:
                                target_file.write(translated_content)

                        except Exception as e:
                            print(f"Error processing {filename}: {str(e)}")
