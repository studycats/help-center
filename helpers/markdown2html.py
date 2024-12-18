import os
from markdown import markdown

for lang in os.listdir('markdown'):
    input_dir = os.path.join('markdown', lang)

    # Skip if not a directory
    if not os.path.isdir(input_dir):
        continue

    output_dir = os.path.join('html', lang)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith('.md'):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace('.md', '.html'))

        with open(input_path, 'r', encoding='utf-8') as input_file:
            text = input_file.read()
        html = markdown(text)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(html)
        
        print(f"Converted {input_path} to {output_path}")
