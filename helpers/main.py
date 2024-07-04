from translate import ArticleTranslator
from download import ZendeskDownloader
from upload import ArticleUploader
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def translate_articles_for_languages(subdomain, languages, email, api_token, time):
    """Creates individual JSON files to hold translations for all articles, for each language in the input dictionary.
    Each file is named using the convention: f'translated_articles_{target_language}.json'.

    Args:
        subdomain (str): The subdomain of the help desk (e.g., 'studycat').
        languages (dict): A dictionary that holds the languages into which the articles will be translated,
                          with the format {language_code: language_name}."""
    
    #Creating instances of the downloader and translators
    downloader = ZendeskDownloader(subdomain, email, api_token, time)
    article_translator = ArticleTranslator()

     # Step 1: Choose if you want to download ALL articles, or just articles after a specified time, to get the 
    # list of all article IDs to download

    # OPTION 1: If you want to download all articles, uncomment code below, and comment out OPTION 2:
    article_ids = downloader.list_all_articles()

    # OPTION 2: If you want to download articles written/updated after a certain time, uncomment code below, 
    # and comment out OPTION 1:
    # article_ids = downloader.list_articles()

    # Step 2: Download articles from Zendesk
    handoff_articles = downloader.download_articles(article_ids)
    
    #Iterating through dictionary
    for lang_code, lang_name in languages.items():
        # Define target language
        target_language = lang_code

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
        print("Attempting upload: ", f'translated_articles_{lang_code}.json')
        article_uploader.trans_upload(f'translated_articles_{lang_code}.json')    

if __name__ == "__main__":

    # Define languages to translate into (code: name)
    # Uncomment each language to run
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
        # 'zh-cn': '简体中文',
        # 'zh-tw': '繁體中文',
    }

    subdomain = 'studycat'
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

    # If choosing to download articles updated after a specific time, change this to the specified time
    # You can find the time in the right format here: https://www.epochconverter.com/
    time = 1719972000
    
    # Translate articles for each language
    translate_articles_for_languages(subdomain, languages, email_address,  api_token, time)

    # # #Uploads the articles to the helpdesk
    upload_articles_for_all(email_address, api_token, subdomain, headers, auth, languages)