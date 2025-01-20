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

def update_categories(categories):
    category_url = f"{url}/categories"

    category_ids = {}
    for category in categories['en']:
        data = {
            "category": {
                "name": category['title'],
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
        print(f'Created category {category['title']}')

    for lang in categories:
        if lang == 'en':
            continue
        for category in categories[lang]:
            translation_url = f"{category_url}/{category_ids[category]}/translations"
            translation_data = {
                "translation": {
                    "title": category['title'],
                    "locale": lang,
                }
            }
            response = requests.post(
                translation_url,
                auth=(f"{ZENDESK_EMAIL_ADDRESS}/token", ZENDESK_API_TOKEN),
                headers=headers,
                json=translation_data
            )
            print(f'Added {lang} translation for category {category['title']}')

    return category_ids
