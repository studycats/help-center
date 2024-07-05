import json
from bs4 import BeautifulSoup
from googletrans import Translator
import re

class ArticleTranslator:
    def __init__(self):
        self.translator = Translator()
        
        self.phrases = ['Learn English', 'Learn Spanish', 'Learn German', 'Learn Chinese', 'Learn French', 'Studycat']
        self.replacements = ['[ENGL]','[ES]','[DTC]','[CH]', '[FRR]', '[STDCT]']


    def substitution(self, text, list_originals, list_replacements):
        """
        Replaces phrases with placeholders before translation and vice versa after translation.

        Args:
            text (str): The text to perform substitution on.
            List_originals (list): The list of original phrases.
            List_replacements (list): The list of replacement placeholders.

        Returns:
            str: The text with phrases substituted.
        """
        for i in range(len(list_originals)):
            # Replace phrases, ignoring case
            replace = re.compile(re.escape(list_originals[i]), re.IGNORECASE)
            text = replace.sub(list_replacements[i], str(text))
        return text
    
    # NEW VERSION
    def translate_text(self, text, target_language):
        """
        Translates the given text to the target language, performing phrase substitution.

        Args:
            text (str): The text to translate.
            target_language (str): The target language code.

        Returns:
            str: The translated text.
        """
        if text.strip():  # Ensure the text is not empty
            # Substitute phrases with placeholders
            text = self.substitution(text, self.phrases, self.replacements)

            translated = self.translator.translate(text, dest=target_language)
            translated_text = translated.text

            # Substitute placeholders back with original phrases
            translated_text = self.substitution(translated.text, self.replacements, self.phrases)
            translated_text = translated_text.replace(".", ". ")
            translated_text = translated_text.replace("!", "! ")
            translated_text = translated_text.replace("?", "? ")
            return translated_text
        return text  # Return the original text if empty
    
   
    def translate_html(self, html_content, target_language):
        """
        Translates the text within an HTML content to the specified target language.

        Args:
            html_content (str): The HTML content to translate.
            target_language (str): The target language code.

        Returns:
            str: The translated HTML content.
        """
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Recursively translate text in HTML elements
        def translate_element(element):
            # If the element is a NavigableString (i.e., actual text), translate it
            if element.name is None:
                try:
                    translated_text = self.translate_text(element.strip(), target_language)
                    return translated_text
                except Exception as e:
                    print(f"Could not translate: {element}, Error: {e}")
                    return element

            # Otherwise, recursively translate the text of child elements
            for child in element.contents:
                translated_child = translate_element(child)
                if isinstance(translated_child, str):
                    child.replace_with(translated_child)
            return element

        # Start translation from the body of the HTML content
        translated_soup = translate_element(soup)
        translated_soup_string = str(translated_soup)
        translated_soup_string = translated_soup_string.replace("<strong>", " <strong>")
        translated_soup_string = translated_soup_string.replace("</strong>", "</strong> ")
        translated_soup_string = translated_soup_string.replace("</strong> ,", "</strong>,")
        translated_soup_string = translated_soup_string.replace("<a", " <a")
        translated_soup_string = translated_soup_string.replace("</a>", " </a> ")

        # Return the translated HTML content as a string
        return translated_soup_string

    def translate_article(self, article, target_language):
        try:
            translated_title = self.translate_text(article['title'], target_language)
            translated_body = self.translate_html(article['body'], target_language)
            
            translated_article = {
                'title': translated_title,
                'body': translated_body,
                'id': article['id']
            }
            return translated_article
        except Exception as e:
            print(f"Error translating article {e}")
            return None

    def translate_articles(self, articles, target_language):
        translated_articles = []
        for article in articles:
            translated_article = self.translate_article(article, target_language)
            if translated_article:
                translated_articles.append(translated_article)
        return translated_articles
    
    def save_to_json(self, translated_articles, output_file, language_code):
        wrapped_content = {language_code: translated_articles}
        with open(output_file, mode='w', encoding='utf-8') as f:
            json.dump(wrapped_content, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__": 
    
    article_to_translate = {
    "body":  "<p><strong>Restart Your Device:</strong></p>\n<ul>\n<li>Sometimes, a simple restart can fix sound issues. Turn off your device completely and then turn it back on.</li>\n</ul>\n</li>\n</ol>\n<p>If you\u2019ve tried all these steps and still can\u2019t hear anything, please <a href=\"https://help.studycat.com/hc/en-us/requests/new\" target=\"_blank\" rel=\"noopener noreferrer\">contact our support team</a>\u00a0for further assistance.</p>",
    "title": "Xoxo",
    "id": 5
  }

    # Initialize translator
    translator = ArticleTranslator()

   # Translate article
    translated_article = translator.translate_article(article_to_translate, target_language='es')

    if translated_article:
        # Output the translated article JSON
        print(json.dumps(translated_article, ensure_ascii=False, indent=2))
    else:
        print("Translation failed.")
