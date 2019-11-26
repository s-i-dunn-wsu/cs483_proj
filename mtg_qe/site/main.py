import os
import cherrypy
from .related_cards import related_cards
from jinja2 import Environment, FileSystemLoader

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
        simple = 0
        template = self.env.get_template('advanced.html')
        return template.render()

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
            'tools.staticdir.dir': os.path.join(os.path.abspath(os.getcwd()), 'styles')
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.abspath(os.getcwd()), 'images')
        },
        '/fonts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.abspath(os.getcwd()), 'fonts')
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
