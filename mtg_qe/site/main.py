import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

corpus = [['Crooked Scales', '4, Tap: Flip a coin. If you win the flip, destroy target creature an opponent controls. If you lose the flip, destroy target creature you control unless you pay 3 and repeat this process.', 'Image.ashx.jpeg'], ['Culling Scales', 'At the beginning of your upkeep, destroy target nonland permanent with the lowest converted mana cost. (If two or more permanents are tied for lowest cost, target any one of them.)', 'Image-1.ashx.jpeg'], ['Dragon Scales', 'Enchanted creature gets +1/+2 and has vigilance. When a creature with converted mana cost 6 or greater enters the battlefield, you may return Dragon Scales from your graveyard to the battlefield attached to that creature.', 'Image-2.ashx.jpeg'], ['Hardened Scales', 'If one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead.', 'Image.ashx.png'], ['Noetic Scales', 'At the beginning of each players upkeep, return to its owners hand each creature that player controls with power greater than the number of cards in their hand.', 'Image-3.ashx.jpeg']]

card = ['Hardened Scales', 'If one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead.', 'Image.ashx.png']

simple = 1

class MTGSearch(object):

    @cherrypy.expose
    def index(self):
        global simple
        simple = 1
        template = env.get_template('index.html')
        return template.render()

    @cherrypy.expose
    def advanced(self):
        global simple
        simple = 0
        template = env.get_template('advanced.html')
        return template.render()

    @cherrypy.expose
    def results(self, searchquery):
        if (searchquery == ''):
            if (simple == 1):
                raise cherrypy.HTTPRedirect('/')
            else:
                raise cherrypy.HTTPRedirect('advanced')

        # Actually get the results
        from ..data import simple_query

        results = simple_query(searchquery)

        # incorperate results into template
        template = env.get_template('results.html')
        return template.render(query=searchquery, result=corpus)


    @cherrypy.expose
    def cardinfo(self, cardid):
        template = env.get_template('cardinfo.html')
        return template.render(id=cardid, carddata=card)

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

def main():
    cherrypy.quickstart(MTGSearch(), '/', conf)

if __name__ == "__main__":
    main()
