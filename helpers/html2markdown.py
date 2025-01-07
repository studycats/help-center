import os, json, configparser
from markdownify import markdownify

folderpath = os.path.join('markdown', 'en')
os.makedirs('markdown', exist_ok=True)
os.makedirs(folderpath, exist_ok=True)

# find the category/section shortcode to create folder structures
def find_level_by_id(level, level_id):
    config = configparser.ConfigParser()
    config.read(os.path.join(level, f'{level}_en.ini'))

    for section in config.sections():
        if config.has_option(section, 'id') and config[section]['id'] == str(level_id):
            return section
    
    return None

with open('articles_en.json') as json_data:
    articles = json.load(json_data)

for article in articles:
    title = article['title']
    # Keep alphanumeric, spaces, and hyphens
    title = ''.join(c for c in title if c.isalnum() or c.isspace() or c == '-')
    title = title.strip().replace(' ', '-')

    category_id = article['category_id']
    section_id = article['section_id']

    category = find_level_by_id('categories', category_id)
    section = find_level_by_id('sections', section_id)

    if not category or not section:
        print(f'Missing category or section for {article['title']}')
        filepath = folderpath
    else:
        filepath = os.path.join(folderpath, category)
        os.makedirs(filepath, exist_ok=True)
        filepath = os.path.join(filepath, section)
        os.makedirs(filepath, exist_ok=True)

    markdown = markdownify(article['body'], hedading_style="ATX")
    # Strip leading/trailing spaces and normalize newlines
    markdown = markdown.strip()
    # Replace 3 or more newlines with 2 newlines
    while '\n\n\n' in markdown:
        markdown = markdown.replace('\n\n\n', '\n\n')

    with open(os.path.join(filepath, f'{title}.md'), 'w') as f:
        f.write('---\n')
        f.write(f'id: {article["id"]}\n')
        f.write(f'title: {article["title"]}\n')
        f.write(f'category: {category}\n')
        f.write(f'section: {section}\n')
        f.write('---\n')
        f.write(markdown)

print('HTML to Markdown conversion complete.')