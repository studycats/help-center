import os, json, requests, configparser
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

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

def get_categories():
    category_url = f"{url}/categories"

    response = requests.get(
        category_url,
        auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
        headers=headers
    )

    if response.status_code == 200:
        return response.json()['categories']
    else:
        print(f"Error fetching categories: {response.status_code}")
        return None

def get_sections():
    section_url = f"{url}/sections"

    response = requests.get(
        section_url,
        auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
        headers=headers
    )

    if response.status_code == 200:
        return response.json()['sections']
    else:
        print(f"Error fetching sections: {response.status_code}")
        return None

def check_name_exists(sections, name):
    for section in sections:
        if section['name'] == name:
            return section['id']
    return False

def create_categories(categories, current):
    category_url = f"{url}/categories"

    category_ids = {}
    for category in categories['en']:
        name = f"Testing {categories['en'][category]['title']}"
        check = check_name_exists(current, name)
        if check:
            print(f"Category {name} already exists")
            category_ids[category] = check
            continue

        data = {
            "category": {
                "name": name,
                "locale": "en-us",
            }
        }

        response = requests.post(
            category_url,
            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
            headers=headers,
            json=data
        )

        category_data = response.json()
        category_ids[category] = category_data['category']['id']
        print(f'Created category {name}')
    
    for lang in categories:
        if lang == 'en':
            continue
        for category in categories[lang]:
            name = f"Testing {categories['en'][category]['title']}"
            check = check_name_exists(current, name)
            if check:
                continue

            translation_url = f"{category_url}/{category_ids[category]}/translations"
            translation_data = {
                "translation": {
                    "title": f"Testing {categories[lang][category]['title']}",
                    "locale": lang,
                }
            }
            response = requests.post(
                translation_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=translation_data
            )
            print(f'Added {lang} translation for category {name}')
    
    return category_ids

def create_sections(sections, current, categories):
    section_url = f"{url}/sections"

    section_ids = {}
    for section in sections['en']:
        name = f"Testing {sections['en'][section]['title']}"
        check = check_name_exists(current, name)
        if check:
            print(f"Section {name} already exists")
            section_ids[section] = check
            continue

        category = sections['en'][section]['category']
        category_id = categories[category]

        data = {
            'section': {
                'name': name,
                'locale': 'en-us',
                'category_id': category_id
            }
        }

        response = requests.post(
            f"{url}/categories/{category_id}/sections",
            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
            headers=headers,
            json=data
        )

        section_data = response.json()
        section_ids[section] = section_data['section']['id']
        print(f'Created section {name}')

    for lang in sections:
        if lang == 'en':
            continue
        for section in sections[lang]:
            name = f"Testing {sections['en'][section]['title']}"
            check = check_name_exists(current, name)
            if check:
                continue

            translation_url = f"{section_url}/{section_ids[section]}/translations"
            translation_data = {
                "translation": {
                    "title": name,
                    "locale": lang,
                }
            }
            response = requests.post(
                translation_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=translation_data
            )
            print(f'Added {lang} translation for section {name}')

    return section_ids

def create_articles(sections):
    # First create English articles and store their IDs
    article_ids = {}
    folder_path = os.path.join('markdown', 'en')
    if os.path.isdir(folder_path):  # Fixed typo in isdir
        for file_name in os.listdir(folder_path):
            if not file_name.endswith('.md'):
                continue
            
            # Get section ID
            file_path = os.path.join('markdown', 'en', file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('section: '):
                        section = line[9:].strip().replace('"', '')
                        break
            section_id = sections[section]

            # Get title
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('title: '):
                        title = line[7:].strip()

            # Get HTML content
            html_path = os.path.join('html', 'en', file_name.replace('.md', '.html'))
            with open(html_path, 'r', encoding='utf-8') as f:
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
            response = requests.post(
                article_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=data
            )
            
            # Store article ID using filename as key
            article_ids[file_name] = response.json()['article']['id']
            print(f'Created English article: {title}')

    # Create translations for other languages
    for lang in os.listdir('markdown'):
        if lang == 'en':
            continue
        folder_path = os.path.join('markdown', lang)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if not file_name.endswith('.md'):
                    continue
                
                # Get title and content for translation
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('title: '):
                            title = line[7:].strip()

                html_path = os.path.join('html', lang, file_name.replace('.md', '.html'))
                with open(html_path, 'r', encoding='utf-8') as f:
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
                    requests.post(
                        translation_url,
                        auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                        headers=headers,
                        json=translation_data
                    )
                    print(f'Added {lang} translation for article: {title}')

    return article_ids

current_categories = get_categories()
current_sections = get_sections()

categories = read_config('categories', ['title', 'id'])
sections = read_config('sections', ['title', 'id', 'category'])

final_categories = create_categories(categories, current_categories)
final_sections = create_sections(sections, current_sections, final_categories)

article = create_articles(final_sections)
