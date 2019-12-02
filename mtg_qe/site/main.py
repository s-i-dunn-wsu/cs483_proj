import os
import cherrypy
from .related_cards import related_cards
from jinja2 import Environment, FileSystemLoader
import json

simple = 1

class MTGSearch(object):
    def __init__(self, env_obj):
        self.env = env_obj

    @cherrypy.expose
    def index(self):
        global simple
        simple = 1
        template = self.env.get_template('index.html')
        return template.render()

    @cherrypy.expose
    def advanced(self):
        global simple
        from .. import data

        simple = 0
        template = self.env.get_template('advanced.html')
        return template.render(expansion_list = data.get_all_sets(),
                               format_list = data.get_all_formats(),
                               type_list = data.get_all_card_types())

    @cherrypy.expose
    def advanced_results(self, page=1, results = 10, **params):
        # need to bridge the keys and values to how advanced_query will expect them.
        # lets start by filtering out empty fields, and converting keys as we go

        # this dict maps keys as they come in through `params` to how advanced_query will
        # align them to the whoosh schema:
        conversions = {
            'type': 'types',
            'subtype': 'subtypes',
            'format': 'legal_formats',
            "expansions": "sets"
        }

        # now filter results, converting to the expected key if possible
        params = {conversions.get(k, k): v for k, v in params.items() if v}

        # now lets handle some special cases:
        # mana options are a bit... awkward because the user may just want cards of a certain color identity
        # or cards with mana symbols in a range. These cases are logically separate-ish to a user, but
        # map to the same fields in our index, so we have to do a bit of data-dancing.
        # if they want cards of a particular color identity `params` will have a 'is_<color>'
        # (as 'on'). If they want cards in a particular range then there will be <color>_[to/from]
        # in params.
        # In the former case what we'll do is send a range '{1 TO }' to whoosh
        # in the latter case (or if both are present as more-specific trumps general)
        # we want to supply the correct range.
        # Lastly: we perform essentially the same steps with power/toughness (we just don't care for 'is_[power/toughness])
        # so to preserve DRY we'll just check for them in the same loop. the first 'if' block will never evaluate to true for
        # these two fields, but the remaining clauses are fine.
        for color in ('white', 'blue', 'red', 'black', 'green', 'power', 'toughness'):
            # First check if 'is_{color}' is present.
            key = f'is_{color}'
            if key in params:
                del params[key]
                params[color] = [1, -1] # advanced_query treats -1 as infinity

            # now check if '{color}_[from/to] is present, if so we want to override
            # what we may have just done.
            a, b = f'{color}_from', f'{color}_to'
            if a in params or b in params:
                params[color] = [int(params.get(a, -1)), int(params.get(b, -1))]

            # now safely clean `a` and `b` out of params
            if a in params:
                del params[a]
            if b in params:
                del params[b]

        # now we pass off to the query method:
        from ..data import advanced_query
        search_results = advanced_query(params, int(page) - 1, results)

        if len(search_results) == 0:
            template = self.env.get_template('no_results.html')
            return template.render(searchquery=str(params))

        last_page = search_results[0].multiverseid == advanced_query(params, int(page), results)[0].multiverseid
        # if (data[0].multiverseid == simple_query(query, False, page_num, results_num)[0].multiverseid)

        template = self.env.get_template('results.html')
        return template.render(searchquery=str(params), result=search_results, pagenum=page, resultsnum=results, lastpage=1 if last_page else 0)


    @cherrypy.expose
    def results(self, query, page = 1, results = 10):
        if (query == ''):
            if (simple == 1):
                raise cherrypy.HTTPRedirect('/')
            else:
                raise cherrypy.HTTPRedirect('advanced')

        # Actually get the results
        from ..data import simple_query

        page_num = int(page)
        results_num = int(results)

        data = simple_query(query, False, page_num - 1, results_num)
        if len(data) == 0:
            template = self.env.get_template('no_results.html')
            return template.render(searchquery=query)

        last = 0
        if (data[0].multiverseid == simple_query(query, False, page_num, results_num)[0].multiverseid):
            last = 1

        # incorperate results into template
        template = self.env.get_template('results.html')
        return template.render(searchquery=query, result=data, pagenum=page_num, resultsnum=results_num, lastpage=last)


    @cherrypy.expose
    def cardinfo(self, cardid):
        template = self.env.get_template('cardinfo.html')
        # Get the card from our 'internal' index.
        from ..data import find_card_by_multiverseid
        card = find_card_by_multiverseid(cardid)

        if card is None:
            print(f"Failed to find card D: ({repr(cardid)})")

        else:
            print(f"card.external_artwork: {card.external_artwork}")

        related = related_cards(card.name, 10)

        return template.render(id=cardid, carddata=card, relatedcards=related)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    old = os.getcwd()
    os.chdir(here)
    env = Environment(loader=FileSystemLoader('templates'))
    conf = {
        '/styles': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(here, 'styles')
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(here, 'images')
        },
        '/fonts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(here, 'fonts')
        },
        "/scripts": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.join(here, "js_scripts")
        }
    }

    try:
        cherrypy.quickstart(MTGSearch(env), '/', conf)
    except Exception as e:
        import traceback as tb
        tb.print_exc(e)
    finally:
        os.chdir(old)

if __name__ == "__main__":
    main()
