import os
from markdown import markdown

for lang in os.listdir('markdown'):
    input_dir = os.path.join('markdown', lang)

    # Skip if not a directory
    if not os.path.isdir(input_dir):
        continue

    output_dir = os.path.join('html', lang)
    os.makedirs(output_dir, exist_ok=True)

    for category in os.listdir(input_dir):
        input_category_dir = os.path.join(input_dir, category)
        output_category_dir = os.path.join(output_dir, category)
        os.makedirs(output_category_dir, exist_ok=True)

        for section in os.listdir(input_category_dir):
            input_section_dir = os.path.join(input_category_dir, section)
            output_section_dir = os.path.join(output_category_dir, section)
            os.makedirs(output_section_dir, exist_ok=True)

            for filename in os.listdir(input_section_dir):
                if not filename.endswith('.md'):
                    continue

                input_path = os.path.join(input_section_dir, filename)
                output_path = os.path.join(output_section_dir, filename.replace('.md', '.html'))

                with open(input_path, 'r', encoding='utf-8') as input_file:
                    text = input_file.read()

                if text.startswith('---'):
                    _, remaining = text.split('---', 2)[1:]
                    text = remaining.strip()

                html = markdown(text)

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(html)
                
                print(f"Converted {input_path} to {output_path}")
