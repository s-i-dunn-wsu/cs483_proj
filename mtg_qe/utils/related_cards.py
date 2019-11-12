# Noah Scarbrough
# CS 483, Fall 2019

import requests
from lxml import html

site = 'https://tappedout.net'

def get_html(url):
    page = requests.get(url)
    return html.fromstring(page.content)

def related_cards(name):
    all_related = []
    counted = []
    paths = related_decks(name)
    print(len(paths))
    for path in paths:
        source = get_html(site + path)
        all_related += source.xpath('//div/ul/li/a/@data-orig')
    for card in all_related:
        if (set(all_related).intersection({card}) != {card}):
            counted += [card]
            
    

def related_decks(name):
    url = site + '/mtg-decks/search/?q=' + name
    source = get_html(url)
    return source.xpath('//div/h3/a/@href')[:3]

if __name__ == '__main__':
    related_cards('Hardened Scales')
