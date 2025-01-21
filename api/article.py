import os, requests
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

def get_article_translations(article_ids):
    current_translations = {}
    for article_id in article_ids:
        translation_url = f"{url}/articles/{article_id}/translations"

        response = requests.get(
            translation_url,
            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
            headers=headers
        ).json()

        current_translations[article_id] = [translation['locale'] for translation in response['translations']]

    return current_translations

def create_articles(sections):
    # First create English articles and store their IDs
    article_ids = {}
    markdown_folder_path = os.path.join('markdown', 'en')
    html_folder_path = os.path.join('html', 'en')
    if os.path.isdir(markdown_folder_path):
        for category in os.listdir(markdown_folder_path):
            markdown_category_folder = os.path.join(markdown_folder_path, category)
            html_category_folder = os.path.join(html_folder_path, category)

            for section in os.listdir(markdown_category_folder):
                markdown_section_folder = os.path.join(markdown_category_folder, section)
                html_section_folder = os.path.join(html_category_folder, section)

                for file_name in os.listdir(markdown_section_folder):
                    if not file_name.endswith('.md'):
                        continue
                    
                    # Get section ID
                    markdown_file_path = os.path.join(markdown_section_folder, file_name)
                    with open(markdown_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('section: '):
                                section = line[9:].strip().replace('"', '')
                                break
                    section_id = sections[section]

                    # Get title
                    with open(markdown_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('title: '):
                                title = line[7:].strip()

                    # Get HTML content
                    html_file_path = os.path.join(html_section_folder, file_name.replace('.md', '.html'))
                    with open(html_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    article_id = None
                    with open(markdown_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('id: '):
                                article_id = line[4:].strip()

                    data = {
                        "article": {
                            "title": title,
                            "body": content,
                            "locale": 'en-us',
                            "user_segment_id": None,
                            "permission_group_id": 1739073,
                        }
                    }

                    if article_id:
                        article_url = f"{url}/articles/{article_id}"

                        response = requests.put(
                            article_url,
                            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                            headers=headers,
                            json=data
                        )

                        article_ids[file_name] = { 'id': article_id, 'is_new': False}
                        print(f'Updated English article: {title}')
                    else:
                        article_url = f"{url}/sections/{section_id}/articles"

                        response = requests.post(
                            article_url,
                            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                            headers=headers,
                            json=data
                        ).json()

                        # Store article ID using filename as key
                        article_id = response['article']['id']
                        article_ids[file_name] = { 'id': article_id, 'is_new': True}
                        print(f'Created English article: {title}')

                        # Update the markdown file with the new ID
                        with open(markdown_file_path, 'r', encoding='utf-8') as f:
                            content = f.readlines()

                        # Insert the ID line right after the first '---'
                        content.insert(1, f'id: {article_id}\n')

                        # Write back to the file
                        with open(markdown_file_path, 'w', encoding='utf-8') as f:
                            f.writelines(content)

    article_id_list = [article['id'] for article in article_ids.values()]
    current_translations = get_article_translations(article_id_list)

    # Create translations for other languages
    for lang in os.listdir('markdown'):
        if lang == 'en':
            continue
        markdown_folder_path = os.path.join('markdown', lang)
        html_path = os.path.join('html', lang)
        if os.path.isdir(markdown_folder_path):
            for category in os.listdir(markdown_folder_path):
                markdown_category_folder = os.path.join(markdown_folder_path, category)
                html_category_folder = os.path.join(html_path, category)

                for section in os.listdir(markdown_category_folder):
                    markdown_section_folder = os.path.join(markdown_category_folder, section)
                    html_section_folder = os.path.join(html_category_folder, section)

                    for file_name in os.listdir(markdown_section_folder):
                        if not file_name.endswith('.md'):
                            continue

                        # Get title and content for translation
                        file_path = os.path.join(markdown_section_folder, file_name)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.startswith('title: '):
                                    title = line[7:].strip()

                        html_file_path = os.path.join(html_section_folder, file_name.replace('.md', '.html'))
                        with open(html_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        translation_data = {
                            "translation": {
                                "title": title,
                                "body": content,
                                "locale": lang,
                            }
                        }

                        # Create translation for the corresponding English article
                        if file_name in article_ids:
                            article_id = article_ids[file_name]['id']
                            translation_url = f"{url}/articles/{article_id}/translations"

                            if article_ids[file_name]['is_new'] and lang not in current_translations[article_id]:
                                requests.post(
                                    translation_url,
                                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                                    headers=headers,
                                    json=translation_data
                                )
                                print(f'Added {lang} translation for article: {title}')
                            else:
                                update_url = f'{translation_url}/{lang}'
                                requests.put(
                                    update_url,
                                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                                    headers=headers,
                                    json=translation_data
                                )
                                print(f'Updated {lang} translation for article: {title}')

    return article_ids