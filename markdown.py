import os, json
from markdownify import markdownify

os.makedirs('markdown', exist_ok=True)

with open('handoff_articles.json') as json_data:
        articles = json.load(json_data)

for article in articles:
        title = article['title'].lower()
        # remove punctuation and turn spaces into dashes
        title = ''.join(c for c in title if c.isalnum() or c.isspace())
        title = title.strip().replace(' ', '-')

        markdown = markdownify(article['body'], heading_style="ATX")

        with open(f'markdown/{title}.md', 'w') as f:
                f.write('---\n')
                f.write(f'title: {article["title"]}\n')
                f.write(f'id: {article["id"]}\n')
                f.write(f'section_id: {article["section_id"]}\n')
                f.write(f'section_name: {article["section_name"]}\n')
                f.write(f'category_id: {article["category_id"]}\n')
                f.write(f'category_name: {article["category_name"]}\n')
                f.write('---\n')
                f.write(markdown)

print('HTML to Markdown conversion complete.')