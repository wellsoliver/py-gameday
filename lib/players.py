from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from re import search
from . import *

class Players(list):
    
    def save(self):
        DB = store.Store()

        for player in self:
            for key in player.keys():
                if player[key] == '' or player[key] == 'null':
                    player[key] = None

            sql = 'REPLACE INTO player (%s) VALUES(%s)' % (','.join(player.keys()), ','.join(['%s'] * len(player.keys())))
            DB.query(sql, player.values())
        
        DB.save()

    def __init__(self, gid, game_id):
        super(Players, self).__init__()

        year, month, day = gid.split('_')[1:4]
        url = '%syear_%s/month_%s/day_%s/%s/%ss/' % (CONSTANTS.BASE, year, month, day, gid, self.type.lower())

        contents = Fetcher.fetch(url)
        if contents is None:
            return

        soup = BeautifulSoup(contents)

        for batter_link in soup.findAll('a'):
            if search(r'\d+\.xml', batter_link['href']):
                batter_url = '%s%s' % (url, batter_link['href'])
                doc = minidom.parseString(Fetcher.fetch(batter_url))
                element = doc.getElementsByTagName('Player').item(0)
                
                player = {}
                for attr in element.attributes.keys():
                    player[attr] = element.attributes[attr].value
                self.append(player)

class Pitchers(Players):

    def __init__(self, gid, game_id):
        self.type = 'PITCHER'
        super(Pitchers, self).__init__(gid, game_id)

class Batters(Players):
    
    def __init__(self, gid, game_id):
        self.type = 'BATTER'
        super(Batters, self).__init__(gid, game_id)

