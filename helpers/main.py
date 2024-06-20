from translate import ArticleTranslator
from download import ZendeskDownloader
from upload import ArticleUploader
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def translate_articles_for_languages(subdomain, languages):
    """Creates individual JSON files to hold translations for all articles, for each language in the input dictionary.
    Each file is named using the convention: f'translated_articles_{target_language}.json'.

    Args:
        subdomain (str): The subdomain of the help desk (e.g., 'studycat').
        languages (dict): A dictionary that holds the languages into which the articles will be translated,
                          with the format {language_code: language_name}."""
    
    #Creating instances of the downloader and translators
    downloader = ZendeskDownloader(subdomain)
    article_translator = ArticleTranslator()

    #Iterating through dictionary
    for lang_code, lang_name in languages.items():
        # Define target language
        target_language = lang_code

        # Step 1: Get the list of article IDs
        article_ids = downloader.list_articles()

        # Step 2: Download articles from Zendesk
        handoff_articles = downloader.download_articles(article_ids)

        # Translate all articles
        translated_articles = article_translator.translate_articles(handoff_articles, target_language=target_language)

        # Determine output file name based on language code
        output_file = f'translated_articles_{target_language}.json'

        # Save translated articles to JSON file
        article_translator.save_to_json(translated_articles, output_file, target_language)

        print(f"Translated articles for {lang_name} saved to '{output_file}'")

def upload_articles_for_all(email_address, api_token, subdomain, headers, auth, target_language_list):
    """Uploads the translated articles for all specified target languages to the helpdesk

    Args:
        email_address (str): The email address used for Zendesk authentication.
        api_token (str): The API token for Zendesk authentication.
        subdomain (str): The subdomain of the Zendesk help desk (e.g., 'studycat').
        target_language_list (dict): A dictionary containing the target languages with the format 
        {language_code: language_name}. """
    
    article_uploader = ArticleUploader(email_address, api_token, subdomain, headers, auth)
    for lang_code, lang_name in target_language_list.items():
        print("trying to upload: ", f'translated_articles_{lang_code}.json')
        article_uploader.trans_upload(f'translated_articles_{lang_code}.json')    

if __name__ == "__main__":

    # Define languages to translate into (code: name)
    languages = {
        # 'de': 'Deutsch',
        # 'es': 'Español',
        # 'fi': 'Suomi',
        # 'fr': 'Français',
        # 'it': 'Italiano',
        # 'ja': '日本語',
        # 'ko': '한국어',
        # 'no': 'Norsk',
        # 'sv': 'svenska',
        # 'zh-CN': '简体中文',
        'zh-TW': '繁體中文'
    }

    subdomain = 'studycat'
    
    # Translate articles for each language
    translate_articles_for_languages(subdomain, languages)

    # Define your email and API token
    email_address = os.getenv("ZENDESK_EMAIL_ADDRESS")
    api_token = os.getenv("ZENDESK_API_TOKEN")

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # Combine email and API token for basic authentication
    auth = (f'{email_address}/token', api_token)

    #Uploads the articles to the helpdesk
    upload_articles_for_all(email_address, api_token, subdomain, headers, auth, languages)