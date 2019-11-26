# Noah Scarbrough
# CS 483, Fall 2019

import os
import random
import requests
from lxml import html
from ..data import find_card_by_name

site = 'https://tappedout.net'

def get_html(url):
    page = requests.get(url)
    return html.fromstring(page.content)

def related_cards(name, amount):
    all_related = []
    counted = []
    max = 1
    paths = related_decks(name, 3)
    results = []
    sorted = [[]]
    if not os.path.exists('../../related_cache'):
        os.mkdir('../../related_cache')
    for path in paths:
        deck_name = path.split('/')[len(path.split('/')) - 2]
        local_path ='../../related_cache/' + deck_name + '.html'
        if os.path.exists(local_path):
            print('Cache exists')
            f = open(local_path)
            source = html.fromstring(f.read())
            f.close()
        else:
            print('Cache does not exist')
            source = get_html(site + path)
            f = open(local_path, 'wb')
            f.write(html.tostring(source))
            f.close()
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
            results.append(find_card_by_name(sorted[max].pop(random.choice(range(len(sorted[max]))))))
        else:
            max -= 1
    return results

def related_decks(name, decks):
    url = site + '/mtg-decks/search/?q=' + name
    source = get_html(url)
    return source.xpath('//div/h3/a/@href')[:decks]

if __name__ == '__main__':
    related_cards('Leyline of Anticipation', 5)
