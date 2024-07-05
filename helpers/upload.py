import json
import requests

class ArticleUploader:
    def __init__(self, email_address, api_token, zendesk_subdomain, headers, auth):
        self.email_address = email_address
        self.api_token = api_token
        self.zendesk_subdomain = zendesk_subdomain
        self.headers = headers
        self.auth = auth

    # Function to check if the translation exists
    def translation_exists(self, article_id, locale):
        url = f'https://{self.zendesk_subdomain}.zendesk.com/api/v2/help_center/articles/{article_id}/translations/{locale}.json'
        response = requests.get(url, headers=self.headers, auth=self.auth)
        return response.status_code == 200

    def add_translations(self, article_id, locale, data):
        # Main logic to decide whether to POST or PUT
        if self.translation_exists(article_id, locale):
            # Use PUT to update the existing translation
            update_url = f'https://{self.zendesk_subdomain}.zendesk.com/api/v2/help_center/articles/{article_id}/translations/{locale}.json'
            response = requests.put(update_url, json=data, headers=self.headers, auth=self.auth)
        else:
            # Use POST to create a new translation
            create_url = f'https://{self.zendesk_subdomain}.zendesk.com/api/v2/help_center/articles/{article_id}/translations.json'
            response = requests.post(create_url, json=data, headers=self.headers, auth=self.auth)

    def trans_upload(self, file_name):
        try:
            with open(file_name, mode='r', encoding='utf-8') as f:
                deliverable = json.load(f)
            print("DELIVERABLE: ", deliverable)
        except FileNotFoundError:
            print(f'The file {file_name} was not found.')
            exit(1)
        except json.JSONDecodeError:
            print(f'The file {file_name} is not a valid JSON file.')
            exit(1)

        for locale in deliverable:
            print("locale: ", deliverable[locale])
            print(f'\n- uploading {locale} translations')
            for article in deliverable[locale]:
                article_id = article['id']
                print("ID: ", article_id)
                data = {
                    'translation': {
                        'locale': locale,
                        'title': article['title'],
                        'body': article['body'],
                        'id': article['id']
                    }
                }
                self.add_translations(article_id, locale, data)

if __name__ == "__main__":
    # Define your Zendesk credentials and subdomain
    email_address = 'integrations@study.cat'
    api_token = 'VvmZEY1KyID4YjDKKzZ4WDzChGkh1UdsNIIOgatm'
    zendesk_subdomain = 'studycat'
    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    auth = (f'{email_address}/token', api_token)

    uploader = ArticleUploader(email_address, api_token, zendesk_subdomain, headers, auth)
    # Specify the file containing translations
    file_name = 'translated_articles_sv.json'
    uploader.trans_upload(file_name)

    