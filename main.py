#! /usr/bin/env python3
import sys
import requests
from cli_colors import *
import argparse
from bs4 import BeautifulSoup


ALL_CLASS = "Ap5OSd"
ALL_CLASS = "Ey4n2"


class Definition:
    meaning = ""
    example = ""
    synonyms = []

    def add_synonyms(self, synonyms_text):
        self.synonyms = synonyms_text.split(": ")[1].split(", ")

    def __str__(self):
        res = ""
        res += f"{color_str(self.meaning, CYAN, MOD_BOLD)}\n"
        if self.example != "":
            res += f"{color_str(self.example, BLUE)}\n"
        if len(self.synonyms) > 0:
            res += f"{color_str('Synonyms:', MAGENTA, MOD_BOLD)}\n"
            for i, syn in enumerate(self.synonyms[:min(3, len(self.synonyms))]):
                color = GREEN_SHADE1
                if i%2 == 1:
                    color = GREEN_SHADE2
                res += f"\t{color_str(syn, color)}\n"
        return res

    def __repr__(self):
        return str(self)

class Section:
    definition_list = None
    title = ""
    def __init__(self, title=None):
        if title is not None:
            self.title = title.capitalize()
        self.definition_list = []
    
    def add_definition(self, definition):
        self.definition_list.append(definition)

    def __repr__(self) -> str:
        res = color_str(self.title, MAGENTA, MOD_BOLD)
        for definition in self.definition_list:
            res += str(definition)
        return res



def get_meanings(soup):
    spelling_attrs = {"id": "scl"}
    sugg = soup.find_all("a", attrs=spelling_attrs)
    spelling_error = False
    if len(sugg) != 0:
        fixes = sugg[0].find_all("i")
        spelling_error = True
        color_print(' '.join([fix.text for fix in fixes]), RED, MOD_BOLD, MOD_SLOW_BLINK)
    main_div_attrs = {"class": "ZINbbc xpd O9g5cc uUPGi"}
    texts_attrs = {"class": ALL_CLASS}
    inner_attrs = {"class": "BNeawe s3v9rd AP7Wnd"}
    first_div = soup.find_all("div", attrs=main_div_attrs)
    first_div = first_div[int(spelling_error)]
    outer_texts = first_div.find_all("div", attrs=texts_attrs)
    inner_texts = []
    for div in outer_texts:
        inner_texts += div.find_all("div", attrs=inner_attrs)

    temp_section = None
    temp_def = None
    sections = []
    texts = [div.text for div in inner_texts]
    for text in texts:
        if len(text) <=1 :
            continue
        num_words = len(text.split())
        if num_words == 1: # Title
            if temp_section is not None:
                if temp_def is not None:
                    temp_section.add_definition(temp_def)
                sections.append(temp_section)
            temp_section = Section(title=text)
            temp_def = None
        elif num_words > 1: # Meaning or Example
            if text.startswith("\"") and text.endswith("\"") or text.startswith("'") and text.endswith("'"):
                if temp_def is None:
                    temp_def = Definition()
                temp_def.example = text
            elif text.startswith("synonyms:"):
                temp_def.add_synonyms(text)
                
            else:
                if temp_def is not None:
                    temp_section.add_definition(temp_def)
                temp_def = Definition()
                temp_def.meaning = text
        
    if temp_section is not None:
            if temp_def is not None:
                temp_section.add_definition(temp_def)
            sections.append(temp_section)
    [print(section) for section in sections]

def get_html_soup(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup

def play_audio(soup: BeautifulSoup):
    audio = soup.find_all("audio")
    if len(audio) == 0:
        color_print("No audio found", YELLOW)
        return
    audio = audio[0]
    
    src = audio["src"]
    import tempfile
    import subprocess
    from shutil import which
    audio_file = requests.get(src).content
    if which("ffplay") is None:
        print(f"{color_str('`ffplay`', RED, MOD_BOLD)} {color_str('not found', RED)}")
        return
    with tempfile.NamedTemporaryFile() as f:
        f.write(audio_file)
        cmd = f"ffplay {f.name} -autoexit -nodisp -volume 5 -loglevel -8".split()
        subprocess.run(cmd)

def print_word_meaning(word, audio):
    url = f"https://www.google.com/search?client=firefox-b-d&q=define+{word}"
    soup = get_html_soup(url)
    get_meanings(soup)
    if audio:
        play_audio(soup)

def main(word, audio=False):
    print_word_meaning(word, audio)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", help="The word that needs defining")
    parser.add_argument("-a", "--audio", action="store_true")
    args = parser.parse_args()
    return args

if __name__=="__main__":
    
    if len(sys.argv) < 2:
        print("missing word\n")
        exit(1)
    args = get_args()
    main(args.word, args.audio)
