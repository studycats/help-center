import os
from markdown import markdown
from bs4 import BeautifulSoup

def style_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    
    for table in tables:
        # Add base table styles
        table['style'] = "height: 125px;"
        
        # Find all rows
        rows = table.find_all('tr')
        for i, row in enumerate(rows):
            row['style'] = f"height: {'25px' if i == 0 else '50px'};"
            
            # Style cells in each row
            cells = row.find_all('td')
            if len(cells) >= 2:  # Ensure we have at least 2 cells
                # First column
                cells[0]['style'] = (
                    "width: 115.938px; "
                    "background: #eef9ff; "
                    "text-align: center; "
                    "border-top: 3px solid #e1f2ff; "
                    "border-bottom: 3px solid #e1f2ff; "
                    "border-left: 3px solid #e1f2ff; "
                    "border-right: none; "
                    f"border-top-left-radius: {('10px' if i == 0 else '0')}; "
                    f"border-bottom-left-radius: {('10px' if i == len(rows)-1 else '0')};"
                )
                
                # Second column
                cells[1]['style'] = (
                    "width: 558.055px; "
                    "border-top: 3px solid #e1f2ff; "
                    "border-right: 3px solid #e1f2ff; "
                    "border-bottom: 3px solid #e1f2ff; "
                    "border-left: none; "
                    f"border-top-right-radius: {('10px' if i == 0 else '0')}; "
                    f"border-bottom-right-radius: {('10px' if i == len(rows)-1 else '0')};"
                )
                
                # Wrap cell content in <p> tags if not already wrapped
                for cell in cells:
                    if not cell.find('p'):
                        content = cell.string
                        cell.string = ''
                        new_p = soup.new_tag('p')
                        if content:
                            new_p.string = content
                        cell.append(new_p)

    return str(soup)

# Main conversion loop
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

                # Convert markdown to HTML
                html = markdown(text, extensions=['tables'])
                html = style_table(html)

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(html)
                
                print(f"Converted {input_path} to {output_path}")
