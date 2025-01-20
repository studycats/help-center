import os, requests
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

# Get all current sections from Zendesk
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

def update_sections(sections, categories):
    section_url = f"{url}/sections"

    section_ids = {}
    for section in sections['en']:
        section_ids[section] = section['id']

        category = section['category']
        category_id = categories[category]

        data = {
            'section': {
                'name': section['title'],
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
        print(f'Updated section {section['title']}')

    for lang in sections:
        if lang == 'en':
            continue
        for section in sections[lang]:
            translation_url = f"{section_url}/{section_ids[section]}/translations"
            translation_data = {
                "translation": {
                    "title": section['title'],
                    "locale": lang,
                }
            }
            response = requests.post(
                translation_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=translation_data
            )
            print(f'Updated {lang} translation for section {section['title']}')

    return section_ids