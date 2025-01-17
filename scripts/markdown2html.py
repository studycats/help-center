import os
from markdown import markdown
from bs4 import BeautifulSoup

def style_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    for table in tables:
        # Add base table styles
        table['style'] = (
            "border-collapse: separate; "  # Needed for border-radius to work
            "border-spacing: 0; "          # Remove gaps between cells
            "border-radius: 3px; "         # Rounded corners for the whole table
            "overflow: hidden; "           # Ensure inner content respects rounded corners
            "padding-bottom: 20px; "
            # "width: 100%; "                # Full width
        )

        # Find all rows
        rows = table.find_all(['tr'])
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            for j, cell in enumerate(cells):
                # Base cell styles
                cell_style = (
                    "border: 1.5px solid #e1f2ff; "  # Light blue border (50% thicker)
                    "padding: 8px; "                 # Inner padding
                )

                # Add background color for header row
                if i == 0:
                    cell_style += (
                        "background-color: #eef9ff; "  # Light blue background
                        "border-top-width: 3px; "      # Thicker top border
                    )

                # Double the bottom border for the last row
                if i == len(rows) - 1:
                    cell_style += "border-bottom-width: 3px; "

                # Double the side borders for first and last cells
                if j == 0:
                    cell_style += "border-left-width: 3px; "
                if j == len(cells) - 1:
                    cell_style += "border-right-width: 3px; "

                cell['style'] = cell_style

    return str(soup)

def style_blockquote(html):
    soup = BeautifulSoup(html, 'html.parser')
    blockquotes = soup.find_all('blockquote')

    for blockquote in blockquotes:
        blockquote['style'] = (
            "background-color: #fff9e6; "  # light yellow background
            "border: 3px solid #ffeb99; "  # dark yellow edge line
            "border-radius: 10px; "  # rounded corners
            "padding: 15px 10px; "  # add some padding for better appearance
            "margin: 10px 5px; "  # add margin for spacing
        )

    return str(soup)

def style_image(html):
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img')

    for image in images:
        # Add style for rounded corners
        image['style'] = (
            "border-radius: 10px; "
            "margin-top: 10px; "
            "margin-bottom: 10px; "
        )

    return str(soup)

def style_list_image(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all images that are descendants of ordered lists
    list_images = soup.select('ol img')

    for img in list_images:
        # Create a new div
        div = soup.new_tag('div')
        div['style'] = (
            "margin-top: 10px; "
            "margin-bottom: 10px; "
        )
        # Replace the image with the div containing the image
        img.wrap(div)

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
                html = style_blockquote(html)
                html = style_image(html)
                html = style_list_image(html)

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(html)

                print(f"Converted {input_path} to {output_path}")
