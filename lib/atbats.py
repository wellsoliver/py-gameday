from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from re import search
from . import *

class Pitch:
	def __init__(self, element, num, count, game_id, pitcher):
		
		self.num = num
		self.game_id = game_id
		self.b = count['balls']
		self.s = count['strikes']
		self.pitcher = pitcher

		for key in element.attributes.keys():
			setattr(self, str(key), element.attributes[key].value)

	def save(self):
		DB = store.Store()

		sql = 'REPLACE INTO pitch (%s) VALUES(%s)' % (','.join(self.__dict__.keys()), ','.join(['%s'] * len(self.__dict__.keys())))
		DB.query(sql, self.__dict__.values())
		DB.save()

class AtBats(list):
	
	def save(self):
		DB = store.Store()
		for inning in self:
			for atbat in inning:
				keys = [k for k in atbat.keys() if k != 'pitches']
				values = [atbat[k] for k in keys]
				
				sql = 'REPLACE INTO atbat (%s) VALUES(%s)' % (','.join(keys), ','.join(['%s'] * len(keys)))
				DB.query(sql, values)
				DB.save()
				
				for pitch in atbat['pitches']:
					pitch.save()
	
	def __init__(self, gid, game_id):
		super(AtBats,self).__init__()

		year, month, day = gid.split('_')[1:4]
		url = '%syear_%s/month_%s/day_%s/%s/inning/' % (CONSTANTS.BASE, year, month, day, gid)
		
		contents = Fetcher.fetch(url)
		if contents is None:
			return
		
		soup = BeautifulSoup(contents)

		inning_num = 1
		for inning_link in soup.findAll('a'):
			if search(r'inning_\d+\.xml', inning_link['href']):
				inning_url = '%s%s' % (url, inning_link['href'])
				doc = minidom.parseString(Fetcher.fetch(inning_url))
				
				inning = []
				
				for atbat in doc.getElementsByTagName('atbat'):
					values = {}
					half = atbat.parentNode.nodeName
					for key in atbat.attributes.keys():
						values[str(key)] = atbat.attributes[key].value

					values['half'] = half
					values['game_id'] = game_id
					values['inning'] = inning_num
					values['pitches'] = []
					
					balls = 0
					strikes = 0
					for pitch in atbat.getElementsByTagName('pitch'):
						count = {'balls': balls, 'strikes': strikes}
						p = Pitch(pitch, atbat.attributes['num'].value, count, game_id, values['pitcher'])
						values['pitches'].append(p)

						if pitch.attributes['type'].value == 'B':
							balls = balls + 1
						elif pitch.attributes['type'].value == 'S':
							strikes = strikes + 1

					inning.append(values)
				self.append(inning)
				inning_num += 1
