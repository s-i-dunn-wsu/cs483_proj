# Noah Scarbrough
# CS 483, Fall 2019

import random
import requests
from lxml import html

site = 'https://tappedout.net'

def get_html(url):
    page = requests.get(url)
    return html.fromstring(page.content)

def related_cards(name, amount):
    all_related = []
    counted = []
    max = 1
    paths = related_decks(name)
    results = []
    sorted = [[]]
    for path in paths:
        source = get_html(site + path)
        all_related += source.xpath('//div/ul/li/a/@data-orig')
    for i in range(len(all_related)):
        sorted.append([])
    for card in all_related:
        if (set(counted).intersection({card}) != {card}):
            counted.append(card)
            sorted[all_related.count(card)].append(card)
            if (all_related.count(card) > max):
                max = all_related.count(card)
    while (len(results) < amount) & (max > 0):
        if (len(sorted[max]) != 0):
            results.append(sorted[max].pop(random.choice(range(len(sorted[max])))))
        else:
            max -= 1
    print(results)

def related_decks(name):
    url = site + '/mtg-decks/search/?q=' + name
    source = get_html(url)
    return source.xpath('//div/h3/a/@href')[:2]

if __name__ == '__main__':
    related_cards('Opposition', 5)
