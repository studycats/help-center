import os, requests
from dotenv import load_dotenv

load_dotenv()

ZENDESK_EMAIL_ADDRESS = os.getenv('ZENDESK_EMAIL_ADDRESS')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
url = "https://studycat.zendesk.com/api/v2/help_center"
headers = { 'Content-Type': 'application/json', }

# Get all current categories from Zendesk
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

def get_category_translations(category_ids):
    current_translations = {}
    for category_id in category_ids:
        translation_url = f"{url}/categories/{category_id}/translations"

        response = requests.get(
            translation_url,
            auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
            headers=headers
        ).json()

        current_translations[category_id] = [translation['locale'] for translation in response['translations']]

    return current_translations

def update_categories(categories):
    category_url = f"{url}/categories"
    category_ids = {}
    for shortcode, category in categories['en'].items():
        data = {
            "category": {
                "name": category['title'],
                "locale": "en-us",
            }
        }

        category_id = category.get('id')
        if category_id:
            update_url = f'{category_url}/{category_id}'

            response = requests.put(
                update_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=data
            )
            category_ids[shortcode] = {
                'id': category_id,
                'is_new': False
            }
            print(f'Updated category {category['title']}')
        else:
            response = requests.post(
                category_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=data
            ).json()

            category_ids[shortcode] = {
                'id': response['category']['id'],
                'is_new': True
            }
            print(f'Created category {category['title']}')

    current_translations = get_category_translations(category_ids)

    for lang in categories:
        if lang == 'en':
            continue
        for shortcode, category in categories[lang].items():
            translation_data = {
                "translation": {
                    "title": category['title'],
                    "locale": lang,
                }
            }
            category_id = category_ids[shortcode]['id']

            if category_ids[shortcode]['is_new'] and lang not in current_translations[category_id]:
                translation_url = f"{category_url}/{category_id}/translations"
                response = requests.post(
                    translation_url,
                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                    headers=headers,
                    json=translation_data
                )
                print(f'Added {lang} translation for category {category['title']}')
            else:
                update_url = f"{category_url}/{category_id}/translations/{lang}"
                response = requests.put(
                    update_url,
                    auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                    headers=headers,
                    json=translation_data
                )
                print(f'Updated {lang} translation for category {category['title']}')

    return { shortcode: data['id'] for shortcode, data in category_ids.items() }
