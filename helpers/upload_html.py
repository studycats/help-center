import os, requests, configparser
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

def post(url, data):
    return requests.post(
        url,
        auth=(f'{ZENDESK_EMAIL_ADDRESS}/token', ZENDESK_API_TOKEN),
        headers=headers,
        json=data
    ).json()

def read_config(folder_path, fields):
    config = configparser.ConfigParser()

    sections = {}
    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.ini'):
            continue

        # Extract language code from filename (e.g. 'en' from 'categories_en.ini')
        lang = file_name.replace('.ini', '').split('_')[-1] if '_' in file_name else ''
        file_path = os.path.join(folder_path, file_name)

        config.read(file_path)

        sections[lang] = {}
        for section in config.sections():
            sections[lang][section] = {}
            for field in fields:
                sections[lang][section][field] = config[section].get(field, '')

    return sections

# levels are either categories or sections
def get_levels(levels):
    levels_url = f"{url}/{levels}"

    response = requests.get(
        levels_url,
        auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
        headers=headers
    )

    if response.status_code == 200:
        return response.json()[levels]
    else:
        print(f"Error fetching {levels}: {response.status_code}")
        return None

def check_name_exists(sections, name):
    for section in sections:
        if section['name'] == name:
            return section['id']
    return False

# levels are either categories or sections
def create_levels(config, current, categories=None):
    ltype = 'section' if categories else 'category'
    level_url = f'{url}/{'sections' if categories else 'categories'}'

    level_ids = {}
    levels = sorted(config.keys(), key=lambda x: (x != 'en', x))
    for lang, levels in config.items():
        english = lang == 'en'
        for level in levels:
            name = f'Testing {level['title']}'
            check = check_name_exists(current, name)
            if check:
                if english:
                    print(f'{ltype.capitalize()} {name} already exists')
                    level_ids[level] = check
                continue

            data = {
                ltype if english else 'translation': {
                    'title': name,
                    'locale': lang
                }
            }

            if english:
                if categories:
                    category = level['category']
                    category_id = categories[category]

                    data[ltype]['category_id'] = category_id
                    final_url = f'{url}/categories/{category_id}/sections', data
                final_url = level_url
            else:
                final_url = f'{level_url}/{level_ids[level]}/translations'

            level_data = post(final_url, data)

            if english:
                level_ids[level] = level_data[ltype]['id']

            print(f'Added {lang} {ltype} {name}')
    
    return level_ids

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

                    article_url = f"{url}/sections/{section_id}/articles"

                    data = {
                        "article": {
                            "title": title,
                            "body": content,
                            "locale": 'en-us',
                            "user_segment_id": None,
                            "permission_group_id": 1739073,
                            "draft": True
                        }
                    }

                    response = post(article_url, data)

                    # Store article ID using filename as key
                    article_ids[file_name] = response['article']['id']
                    print(f'Created English article: {title}')

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

                        # Create translation for the corresponding English article
                        if file_name in article_ids:
                            article_id = article_ids[file_name]
                            translation_url = f"{url}/articles/{article_id}/translations"
                            translation_data = {
                                "translation": {
                                    "title": title,
                                    "body": content,
                                    "locale": lang,
                                    "draft": True
                                }
                            }

                            post(translation_url, json=translation_data)
                            print(f'Added {lang} translation for article: {title}')

    return article_ids

current_categories = get_levels('categories')
current_sections = get_levels('sections')

categories = read_config('categories', ['title', 'id'])
sections = read_config('sections', ['title', 'id', 'category'])

final_categories = create_levels(categories, current_categories)
final_sections = create_levels(sections, current_sections, final_categories)

article = create_articles(final_sections)
