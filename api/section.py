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

def get_section_translations(section_ids):
    current_translations = {}
    for section_id in section_ids:
        translation_url = f"{url}/sections/{section_id}/translations"

        response = requests.get(
            translation_url,
            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
            headers=headers
        ).json()

        current_translations[section_id] = [translation['locale'] for translation in response['translations']]

    return current_translations

def update_sections(sections, categories):
    section_url = f"{url}/sections"

    section_ids = {}
    for shortcode, section in sections['en'].items():
        section_ids[shortcode] = section['id']

        category = section['category']
        category_id = categories[category]

        data = {
            'section': {
                'name': section['title'],
                'locale': 'en-us',
                'category_id': category_id
            }
        }

        section_id = section.get('id')
        if section_id:
            response = requests.put(
                f'{url}/sections/{section_id}',
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=data
            )
            section_ids[shortcode] = {
                'id': section_id,
                'is_new': False
            }
            print(f'Updated section {section['title']}')
        else:
            response = requests.post(
                f"{url}/categories/{category_id}/sections",
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=data
            ).json()

            section_ids[shortcode] = {
                'id': response['section']['id'],
                'is_new': True
            }
            print(f'Created section {section['title']}')

    current_translations = get_section_translations(section_ids)

    for lang in sections:
        if lang == 'en':
            continue
        for shortcode, section in sections[lang].items():
            translation_data = {
                "translation": {
                    "title": section['title'],
                    "locale": lang,
                }
            }
            section_id = section_ids[shortcode]['id']

            if section_ids[shortcode]['is_new'] and lang not in current_translations[section_id]:
                translation_url = f"{section_url}/{section_id}/translations"

                response = requests.post(
                    translation_url,
                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                    headers=headers,
                    json=translation_data
                )
                print(f'Added {lang} translation for section {section['title']}')
            else:
                update_url = f"{section_url}/{section_id}/translations/{lang}"
                response = requests.put(
                    update_url,
                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                    headers=headers,
                    json=translation_data
                )
                print(f'Updated {lang} translation for section {section['title']}')

    return { shortcode: data['id'] for shortcode, data in section_ids.items() }