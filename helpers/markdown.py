import os, json, configparser
from markdownify import markdownify

os.makedirs('markdown', exist_ok=True)

with open('handoff_articles.json') as json_data:
        articles = json.load(json_data)
        # print(articles)

groupings = {
        "sections": {},  # id -> name mapping
        "categories": {},  # id -> name mapping
}

for article in articles:
        title = article['title'].lower()
        # remove punctuation and turn spaces into dashes
        title = ''.join(c for c in title if c.isalnum() or c.isspace())
        title = title.strip().replace(' ', '-')

        markdown = markdownify(article['body'], heading_style="ATX")

        groupings["sections"][article["section_id"]] = article["section_name"]
        groupings["categories"][article["category_id"]] = article["category_name"]

        with open(os.path.join('markdown', f'{title}.md'), 'w') as f:
                f.write('---\n')
                f.write(f'title: {article["title"]}\n')
                f.write(f'id: {article["id"]}\n')
                f.write(f'section_id: {article["section_id"]}\n')
                f.write(f'section_name: {article["section_name"]}\n')
                f.write(f'category_id: {article["category_id"]}\n')
                f.write(f'category_name: {article["category_name"]}\n')
                f.write('---\n')
                f.write(markdown)

# Create configparser instance
config = configparser.ConfigParser()

# Add sections to the config
config['Sections'] = {str(article['section_id']): article['section_name'] for article in articles}
config['Categories'] = {str(article['category_id']): article['category_name'] for article in articles}

# Write to INI file
with open('groupings.ini', 'w') as configfile:
    config.write(configfile)

print('Groupings saved to groupings.ini')

print('HTML to Markdown conversion complete.')