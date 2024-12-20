import os, json
from markdownify import markdownify

os.makedirs('markdown', exist_ok=True)

with open('handoff_articles.json') as json_data:
        articles = json.load(json_data)
        # print(articles)

for article in articles:
        title = article['title'].lower()
        # remove punctuation and turn spaces into dashes
        title = ''.join(c for c in title if c.isalnum() or c.isspace())
        title = title.strip().replace(' ', '-')

        markdown = markdownify(article['body'], heading_style="ATX")

        with open(os.path.join('markdown', 'en', f'{title}.md'), 'w') as f:
                f.write('---\n')
                f.write(f'title: {article["title"]}\n')
                f.write(f'category: {article["category_name"]}\n')
                f.write(f'section: {article["section_name"]}\n')
                f.write('---\n')
                f.write(markdown)

print('HTML to Markdown conversion complete.')