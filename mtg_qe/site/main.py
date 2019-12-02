import os
import cherrypy
from .related_cards import related_cards
from ..utils.mana import replace_curly_brackets_in_text, curly_bracket_to_img_link
from jinja2 import Environment, FileSystemLoader
import json

simple = 1

class MTGSearch(object):
    def __init__(self, env_obj):
        self.env = env_obj

        # Associate error handlers:
        cherrypy.config.update({'error_page.404':self.on_404})

    def on_404(self, status, message, traceback, version):
        template = self.env.get_template('error_404.html')
        return template.render()

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
    def advanced_results(self, page=1, results = 10, decode=False, **params):
        # if decode is false, then we need to pay special attention to the values in params
        # otherwise we may assume that params contains a field 'query' which can be
        # json deserialized to what we'll pass to advanced_query.

        # convert page and results to ints incase they aren't
        page = int(page)
        results = int(results)

        if decode == False:
            print("tweaking stuff")
            params = self._tweak_adv_params(params)
            print(params)


        else:
            # get the serialized query from params:
            params = json.loads(params['query'])
            print("Search parameters: " + str(params))

        if not params:
            raise cherrypy.HTTPRedirect("/advanced")

        # now we pass off to the query method:
        from ..data import advanced_query
        search_results = advanced_query(params, int(page) - 1, results)

        if len(search_results) == 0:
            template = self.env.get_template('no_results.html')
            return template.render(searchquery=str(params))

        # Check if this is the last page by comparing the first entry on this page to the first on the next.
        last_page = search_results[0].multiverseid == advanced_query(params, int(page), results)[0].multiverseid

        # inflate and return the template.
        template = self.env.get_template('advanced_results.html')
        return template.render(searchquery=json.dumps(params), result=search_results,
                               pagenum=page, resultsnum=results, lastpage=1 if last_page else 0,
                               art_locator=self._locate_art_for_card,
                               mana_symbol_fixer=replace_curly_brackets_in_text)


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
        return template.render(searchquery=query, result=data,
                               pagenum=page_num, resultsnum=results_num,
                               lastpage=last, art_locator=self._locate_art_for_card,
                               mana_symbol_fixer=replace_curly_brackets_in_text)


    @cherrypy.expose
    def cardinfo(self, cardid):
        template = self.env.get_template('cardinfo.html')
        # Get the card from our 'internal' index.
        from ..data import find_card_by_multiverseid
        card = find_card_by_multiverseid(cardid)

        if card is None:
            print(f"Failed to find card D: ({repr(cardid)})")
            raise cherrypy.HTTPError(404)

        else:
            print(f"card.external_artwork: {card.external_artwork}")

        related = related_cards(card.name, 10)

        # prep some fields that need some processing
        mana_cost = None if card.mana_cost is None else "".join([curly_bracket_to_img_link(x) for x in card.mana_cost])
        rules_text = None if card.text is None else replace_curly_brackets_in_text(card.text)

        return template.render(id=cardid, carddata=card,
                                relatedcards=related,
                                artwork=self._locate_art_for_card(card),
                                mana_cost = mana_cost,
                                rules_text = rules_text)

    def _locate_art_for_card(self, card):
        """
        Determines if we have local artwork loaded for this card, if we do it provides a link to that
        if not, it will provide an external link to the cards artwork.
        """
        from ..data import get_data_location
        local_path = os.path.join(get_data_location(), 'artwork', card.local_artwork)
        if os.path.exists(local_path):
            return '/'.join(['/card_art', card.local_artwork])

        else:
            return "https://gatherer.wizards.com" + card.external_artwork


    def _tweak_adv_params(self, params):
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
        new_params = {conversions.get(k, k): v for k, v in params.items() if v}

        # now lets handle some special cases:
        # mana options are a bit... awkward because the user may just want cards of a certain color identity
        # or cards with mana symbols in a range. These cases are logically separate-ish to a user, but
        # map to the same fields in our index, so we have to do a bit of data-dancing.
        # if they want cards of a particular color identity `params` will have a 'is_<color>'
        # (as 'on'). If they want cards in a particular range then there will be <color>_[to/from]
        # in new_params.
        # In the former case what we'll do is send a range '{1 TO }' to whoosh
        # in the latter case (or if both are present as more-specific trumps general)
        # we want to supply the correct range.
        # Lastly: we perform essentially the same steps with power/toughness (we just don't care for 'is_[power/toughness])
        # so to preserve DRY we'll just check for them in the same loop. the first 'if' block will never evaluate to true for
        # these two fields, but the remaining clauses are fine.
        for color in ('white', 'blue', 'red', 'black', 'green', 'power', 'toughness', 'cmc'):
            # First check if 'is_{color}' is present.
            key = f'is_{color}'
            if key in new_params:
                del new_params[key]
                new_params[color] = [1, -1] # advanced_query treats -1 as infinity

            # now check if '{color}_[from/to] is present, if so we want to override
            # what we may have just done.
            a, b = f'{color}_from', f'{color}_to'
            if a in new_params or b in new_params:
                new_params[color] = [int(new_params.get(a, -1)), int(new_params.get(b, -1))]

            # now safely clean `a` and `b` out of params
            if a in new_params:
                del new_params[a]
            if b in new_params:
                del new_params[b]

        # next: since there are two 'types' input fields, they get provided as a list
        # however, we want them as a comma or space separated string.
        if 'types' in new_params:
            if any(new_params['types']):
                new_params['types'] = " ".join([x for x in new_params['types'] if x])
            else:
                del new_params['types']
        # Return the tweaked content
        return new_params


def main():
    from ..data import get_data_location
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
        },
        "/card_art": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.join(get_data_location(), 'artwork')
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
