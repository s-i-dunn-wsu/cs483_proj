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
    # Scrape related cards from tappedout
    if not os.path.exists(os.path.dirname(__file__) + '/../data/related_cache'):
        os.mkdir(os.path.dirname(__file__) + '/../data/related_cache')
    for path in paths:
        deck_name = path.split('/')[len(path.split('/')) - 2]
        local_path = os.path.dirname(__file__) + '/../data/related_cache/' + deck_name + '.html'
        if os.path.exists(local_path):
            print('Cache exists')
            f = open(local_path)
            source = html.fromstring(f.read())
            f.close()
        else:
            print('Cache does not exist')
            try:
                source = get_html(site + path)
            except requests.exceptions.ConnectionError:
                return []
            else:
                f = open(local_path, 'wb')
                f.write(html.tostring(source))
                f.close()
        all_related += source.xpath('//div/ul/li/a/@data-orig')
    # Form 2D array: sorted[occurances][array of card names]
    for i in range(len(all_related)):
        sorted.append([])
    for card in all_related:
        if (set(counted).intersection({card}) != {card}):
            counted.append(card)
            sorted[all_related.count(card)].append(card)
            if (all_related.count(card) > max):
                max = all_related.count(card)
    # Get list of most common occurences
    while (len(results) < amount) & (max > 0):
        if sorted == [[]]:
            return []
        if (len(sorted[max]) != 0):
            new_card_name = sorted[max].pop(random.choice(range(len(sorted[max]))))
            new_card = find_card_by_name(new_card_name)
            if new_card is not None:
                # Disallow card being related to itself
                if (new_card != find_card_by_name(name) and new_card.name not in ['Mountain', 'Island', 'Plains', 'Forest', 'Swamp']):
                    results.append(new_card)
            else:
                print('Card ' + new_card_name + ' does not exist.')
        else:
            max -= 1
    return results

def related_decks(name, decks):
    url = site + '/mtg-decks/search/?q=' + name
    try:
        source = get_html(url)
    except requests.exceptions.ConnectionError:
        return []
    else:
        return source.xpath('//div/h3/a/@href')[:decks]

if __name__ == '__main__':
    related_cards('The Great Henge', 5)
