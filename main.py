#!/usr/bin/python3
import sys
import re
import requests
from bs4 import BeautifulSoup

DIV_CLASS="e16867sm0"
SECTION_CLASS="e1hk9ate0"
MEANING_CLASS="e1q3nk1v4"
LUNA_LABEL_CLASS="luna-label"

COLORS = ['\033[1;31m', '\033[1;32m']
TITLE_COLOR = '\033[1;35m'
RESET_COLOR = '\033[0m'


def get_meanings(main_div):
    attrs = {
            "class": MEANING_CLASS
            }
    meanings = main_div.find_all("span", attrs=attrs)
    return meanings

def get_main_div(soup):
    attrs = {
            "class": DIV_CLASS
            }
    main_div = soup.find("div", attrs=attrs)
    return main_div

def extract_text(tag):
     contents = tag.contents
     ret = []
     pattern = r'<.+?>(.*)</.+?>'
     if contents is None:
         return None
     for content in contents:
         nested_tags = re.findall(pattern, str(content))
         if len(nested_tags) > 0:
             [ret.append(text) for text in
                     extract_text(BeautifulSoup(
                         nested_tags[0], 'html.parser'))]
         else:
             ret.append(content)
     
     return ret

def get_html_soup(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup

def print_word_meaning(word):
    url = f"https://www.dictionary.com/browse/{word}"
    soup = get_html_soup(url)
    main_div = get_main_div(soup)
    meanings = get_meanings(main_div)
    print_meanings(meanings)

def print_meanings(meanings):
    attrs = {
            "class": LUNA_LABEL_CLASS
            }
    for i, meaning in enumerate(meanings):
        title = meaning.find('span', attrs=attrs)
        if title is not None:
            print(f"\n{TITLE_COLOR}{title.contents[0]}{RESET_COLOR}:")
        else:
            text = ''.join(extract_text(meaning))
            print(f"{COLORS[i%2]}{text}{RESET_COLOR}")

def main(word):
    print_word_meaning(word)


if __name__=="__main__":
    if len(sys.argv) < 2:
        print("missing word\n")
        exit(1)

    main(sys.argv[1])
