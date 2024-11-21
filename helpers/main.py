from translate import ArticleTranslator
from download import ZendeskDownloader
from upload import ArticleUploader
import os
from dotenv import load_dotenv
import sys
import arrow

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

    # Step 1: Choosing if you want to download ALL articles, or just articles after a specified time, to get the 
    # list of all article IDs to download
    if(time == 0):
        # OPTION 1: If you want to download all articles
        article_ids = downloader.list_all_articles()
    else:
        # OPTION 2: If you want to download articles written/updated after a certain time,
        article_ids = downloader.list_articles()
    
    # Step 2: Downloading articles from Zendesk
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
    else:
        print('No languages specified for translation')

def upload_articles(email_address, api_token, subdomain, headers, auth, target_language_list):
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

    while True:
        # Define languages to translate into (code: name)
        # Uncomment each language to run
        languages = {
            'da': 'Danish',
            'de': 'German',
            'es': 'Spanish',
            'fi': 'Finnish',
            'fr': 'French',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ms': 'Malay',
            'no': 'Norweigan',
            'pt-PT': 'Portugese',
            'ru': 'Russian',
            'sv': 'Swedish',
            'vi': 'Vietnamese',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
        }

        # Display available languages
        print("Available languages for translation:")
        print("Type 'all' to translate into all languages")
        print("Or 'none' to only download English articles")

        for code, name in languages.items():
            print(f"{code}: {name}")
            
        # Prompt user for language code
        language_code = input("Enter the language code for translation: ").strip()

        if language_code in languages:
            chosen_languages = {language_code: languages[language_code]}
            language_name = str(languages[language_code])
            print("Chosen language: ", language_name)
        elif language_code.lower() == 'all':
            chosen_languages = languages
            language_name = 'all languages'
            print("Chosen all languages")
        elif language_code.lower() == 'none':
            chosen_languages = {}
            language_name = 'no languages'
            print('Downloading English artiles only')
        else:
            print(f"Language code {language_code} is not supported.")
            sys.exit(1)

        # Prompt user for download option
        print("Choose download option:")
        print("1: Download all articles")
        print("2: Download articles written/updated after a specific date and time")
        download_option = input("Enter your choice (1 or 2): ").strip()

        if download_option == "1":
            time = 0
        elif download_option == "2":
            # Prompt user for date and time
            print("Please enter the date and time in Taiwan's timezone (CST).")
            date_str = input("Enter the date (YYYY-MM-DD): ").strip()
            time_str = input("Enter the time (HH:MM): ").strip()

            # Combine date and time into a single string
            datetime_str = f"{date_str} {time_str}"

            # Convert the combined string to epoch time
            try:
                time = arrow.get(datetime_str, 'YYYY-MM-DD HH:mm', tzinfo='Asia/Taipei').timestamp()
                time = int(time)
                # print(f"Converted date and time to epoch time: {time}")
            except arrow.parser.ParserError:
                print("Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
                sys.exit(1)
        else:
            print("Invalid choice. Please enter 1 or 2.")
            sys.exit(1)

        # Translate articles for each language
        translate_articles_for_languages(subdomain, chosen_languages, email_address,  api_token, time)

        # #Uploads the articles to the helpdesk
        # upload_articles(email_address, api_token, subdomain, headers, auth, chosen_languages)

        print("-----------------------------------------------------------------")
        print("Translations for", language_name, "were successfully uploaded.")
        print("-----------------------------------------------------------------")


        # Ask if the user wants to translate and upload for another language
        another_language = input("Would you like to translate and upload articles for another language? (yes/no): ").strip().lower()
        if another_language != 'yes':
            print("Thank you, bye! 😊")
            break
