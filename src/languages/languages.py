import json
import glob
#List of languages from json files
languages = {}
language_list = glob.glob("src/languages/*.json")

for lang in language_list:
        filename = lang.split('\\')
        lang_code = filename[1].split('.')[0]

        with open(lang, 'r', encoding='utf8') as file:
                languages[lang_code] = json.loads(file.read())