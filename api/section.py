import os, requests
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

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

def create_sections(sections, categories):
    current = get_sections()
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