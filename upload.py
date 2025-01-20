import os, configparser
from api.category import update_categories
from api.section import update_sections
from api.article import create_articles

def read_config(folder_path, fields):
    config = configparser.ConfigParser()

    sections = {}
    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.ini'):
            continue

        # Extract language code from filename (e.g. 'en' from 'categories_en.ini')
        lang = file_name.replace('.ini', '').split('_')[-1] if '_' in file_name else ''
        file_path = os.path.join(folder_path, file_name)

        config.read(file_path)

        sections[lang] = {}
        for section in config.sections():
            sections[lang][section] = {}
            for field in fields:
                sections[lang][section][field] = config[section].get(field, '')

    return sections

categories = read_config('categories', ['title', 'id'])
sections = read_config('sections', ['title', 'id', 'category'])

final_categories = update_categories(categories)
final_sections = update_sections(sections, final_categories)

article = create_articles(final_sections)