#!/usr/bin/python3
import sys
import re
import requests
from bs4 import BeautifulSoup


SECTION_CLASS = "pgRvse vdBwhd ePtbIe"
SECTION_JSNAME = "r5Nvmf"
DEFINITION_CLASS = "L1jWkf h3TRxf"

ALL_CLASS = "Ap5OSd"


COLORS = ['\033[1;31m', '\033[1;32m']
TITLE_COLOR = '\033[1;35m'
RESET_COLOR = '\033[0m'


class Definition:
    meaning = ""
    example = ""
    def __init__(self, soup=None):
        if soup is not None:
            self.get_meaning(soup)
            self.get_example(soup)
    
    def _get_meaning(self, soup):
        attrs = {"data_dobid": "dfn"}
        meaning_div = soup.find_all("div", attrs=attrs)
        if meaning_div is not None:
            self.meaning = meaning_div[0].text
    
    def _get_example(self, soup):
        attrs = {"class": "H9KYcb"}
        meaning_div = soup.find_all("div", attrs=attrs)
        if meaning_div is not None:
            self.meaning = meaning_div[0].text

    def __str__(self):
        return f"Meaning: {self.meaning}\nExample: {self.example}"

    def __repr__(self):
        return f"Meaning: {self.meaning}\nExample: {self.example}"

class Section:
    definition_list = None
    title = ""
    def __init__(self, section_soup=None):
        if section_soup is not None:
            self.get_title(section_soup)
            self.fill_definitions(section_soup)    
        self.definition_list = []
    def get_title(self, soup):
        attrs = {"class": SECTION_CLASS}
        name_div = soup.find_all("div", attrs=attrs)
        if name_div is not None:
            self.title = name_div[0].text

    def fill_definitions(self, soup):
        attrs = {"class": DEFINITION_CLASS}
        definition_divs = soup.find_all("div", attrs=attrs)
        if definition_divs is not None:
            self.definition_list = map(lambda definition: Definition(definition), definition_divs)
    
    def __repr__(self) -> str:
        return f"Title: {self.title}\nDefinitions:\n{self.definition_list}"

def get_meanings(soup):
    section_attributes = {"jsname": SECTION_JSNAME}
    sections = soup.find_all("div", attrs=section_attributes)
    if len(sections) != 0:
        sections = list(map(lambda section: Section(section), sections))
        print(sections)
    else:
        raise("Sections not found")


def get_meanings_flat(soup):
    texts_attrs = {"class": ALL_CLASS}
    inner_attrs = {"class": "BNeawe s3v9rd AP7Wnd"}
    grey_inner_attrs = {"class": "r0bn4c rQMQod"}
    outer_texts = soup.find_all("div", attrs=texts_attrs)
    temp_section = None
    sections = []
    for outer_text in outer_texts:
        inner_divs = outer_text.find_all("div", attrs=inner_attrs)
        inner_count = len(inner_divs)
        if inner_count == 0:
            continue
        if inner_count == 1:
            if temp_section is not None:
                if temp_section.title == "" or len(temp_section.definition_list) == 0:
                    pass
                else:
                    sections.append(temp_section)
            temp_section = Section()
            inner_div = inner_divs[0]
            grey_div = inner_div.find_all("span", attrs=grey_inner_attrs)
            if len(grey_div) != 0:
                temp_section.title = grey_div[0].text
        if inner_count > 1:
            meaning = ""
            example = ""
            for inner_div in inner_divs:
                grey_div = inner_div.find_all("span", attrs=grey_inner_attrs)
                if len(grey_div) == 0:
                    text = inner_div.text
                    if len(text) > 1:
                        meaning = text
                else:
                    text = grey_div[0].text
                    example = text
                if len(meaning) > 1 and len(example) > 1:
                    temp_def = Definition()
                    temp_def.example = example
                    temp_def.meaning = meaning
                    temp_section.definition_list.append(temp_def)
                    
    if temp_section is not None:
        if temp_section.title == "" or len(temp_section.definition_list) == 0:
            pass
        else:
            sections.append(temp_section)
    [print(section, "\n") for section in sections]


def get_html_soup(url):
    html_text = requests.get(url).text
    with open("out2.html", "w") as f:
        f.write(html_text)
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup

def print_word_meaning(word):
    url = f"https://www.google.com/search?client=firefox-b-d&q=define+{word}"
    soup = get_html_soup(url)
    meanings = get_meanings_flat(soup)
    # print_meanings(meanings)

# def print_meanings(meanings):
#     attrs = {
#             "class": LUNA_LABEL_CLASS
#             }
#     for i, meaning in enumerate(meanings):
#         title = meaning.find('span', attrs=attrs)
#         if title is not None:
#             print(f"\n{TITLE_COLOR}{title.contents[0]}{RESET_COLOR}:")
#         else:
#             text = ''.join(extract_text(meaning))
#             print(f"{COLORS[i%2]}{text}{RESET_COLOR}")

def main(word):
    print_word_meaning(word)


if __name__=="__main__":
    if len(sys.argv) < 2:
        print("missing word\n")
        exit(1)

    main(sys.argv[1])
