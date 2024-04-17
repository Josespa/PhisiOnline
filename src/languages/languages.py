import json
import glob
#List of languages from json files
languages = {}
language_list = glob.glob("src/languages//*.json")
#print(language_list)
languages_codes = []
for lang in language_list:
        filename = lang.split('/')
        if '\\' in lang:
                filename = lang.split('\\')
        else:
                filename = lang.split('/')
        for file_split in filename:
                if '.json' in file_split:
                        lang_code = file_split.split('.')[0]
        languages_codes.append(lang_code)
        with open(lang, 'r', encoding='utf8') as file:
                languages[lang_code] = json.loads(file.read())