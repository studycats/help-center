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
        title = '-'.join([title, str(article['id'])])

        markdown = markdownify(article['body'], heading_style="ATX")

        with open(f'markdown/{title}.md', 'w') as f:
            f.write(markdown)

print('HTML to Markdown conversion complete.')