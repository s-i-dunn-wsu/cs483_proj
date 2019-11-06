import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

corpus = [['Crooked Scales', '4, Tap: Flip a coin. If you win the flip, destroy target creature an opponent controls. If you lose the flip, destroy target creature you control unless you pay 3 and repeat this process.', 'Image.ashx.jpeg'], ['Culling Scales', 'At the beginning of your upkeep, destroy target nonland permanent with the lowest converted mana cost. (If two or more permanents are tied for lowest cost, target any one of them.)', 'Image-1.ashx.jpeg'], ['Dragon Scales', 'Enchanted creature gets +1/+2 and has vigilance. When a creature with converted mana cost 6 or greater enters the battlefield, you may return Dragon Scales from your graveyard to the battlefield attached to that creature.', 'Image-2.ashx.jpeg'], ['Hardened Scales', 'If one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead.', 'Image.ashx.png'], ['Noetic Scales', 'At the beginning of each players upkeep, return to its owners hand each creature that player controls with power greater than the number of cards in their hand.', 'Image-3.ashx.jpeg']]

card = ['Hardened Scales', 'If one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead.', 'Image.ashx.png']

class MTGSearch(object):
    @cherrypy.expose
    def index(self):
        template = env.get_template('index.html')
        return template.render()
    
    @cherrypy.expose
    def results(self, searchquery):
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

cherrypy.quickstart(MTGSearch(), '/', conf)
