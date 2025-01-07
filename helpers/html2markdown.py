import os, json
from markdownify import markdownify

filepath = os.path.join('markdown', 'source')
os.makedirs('markdown', exist_ok=True)
os.makedirs(filepath, exist_ok=True)

with open('articles_en.json') as json_data:
        articles = json.load(json_data)

for article in articles:
        article_id = article['id']
        title = article['title']
        # Keep alphanumeric, spaces, and hyphens
        title = ''.join(c for c in title if c.isalnum() or c.isspace() or c == '-')
        title = title.strip().replace(' ', '-')

        markdown = markdownify(article['body'], hedading_style="ATX")
        # Strip leading/trailing spaces and normalize newlines
        markdown = markdown.strip()
        # Replace 3 or more newlines with 2 newlines
        while '\n\n\n' in markdown:
            markdown = markdown.replace('\n\n\n', '\n\n')

        with open(os.path.join(filepath, f'{article_id}-{title}.md'), 'w') as f:
                f.write('---\n')
                f.write(f'title: {article["title"]}\n')
                f.write(f'category: {article["category_name"]}\n')
                f.write(f'section: {article["section_name"]}\n')
                f.write('---\n')
                f.write(markdown)
                f.write('\n[EOF]')

print('HTML to Markdown conversion complete.')