from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from re import search
from . import *

class Pitch:
	def __init__(self, element, count, **kwargs):

		values = {}
		values['num'] = kwargs['num'] if 'num' in kwargs else None
		values['game_id'] = kwargs['game_id'] if 'game_id' in kwargs else None
		values['pitcher'] = kwargs['pitcher'] if 'pitcher' in kwargs else None
		values['batter'] = kwargs['batter'] if 'batter' in kwargs else None
		values['b'] = count['balls']
		values['s'] = count['strikes']
		
		# these change a lot :(
		# tired of taking them from the XML element
		# because maybe I don't have them in the schema
		FIELDS = ['des','id','type','x','y','on_1b','on_2b','on_3b','sv_id','start_speed',
			'end_speed','sz_top','sz_bot','pfx_x','pfx_z','px','pz','x0','y0','z0','vx0','vy0','vz0',
			'ax','ay','az','break_y','break_angle','break_length','pitch_type','type_confidence',
			'spin_dir','spin_rate','zone']

		for key in element.attributes.keys():
			if key in FIELDS:
				values[key] = element.attributes[key].value
		
		self.values = values

	def save(self):
		DB = store.Store()

		sql = 'REPLACE INTO pitch (%s) VALUES(%s)' % (','.join(self.values.keys()), ','.join(['%s'] * len(self.values)))
		DB.query(sql, self.values.values())
		DB.save()

class AtBats(list):
	
	def save(self):
		DB = store.Store()
		for inning in self:
			for atbat in inning:
				keys = [k for k in atbat.keys() if k != 'pitches']
				values = [None if atbat[k] == '' else atbat[k] for k in keys]
				
				sql ='REPLACE INTO atbat (%s) VALUES(%s)' % (','.join(keys), ','.join(['%s'] * len(keys)))
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
						kwargs = {'game_id': game_id,
							'batter': values['batter'],
							'pitcher': values['pitcher'],
							'num': atbat.attributes['num'].value}
						p = Pitch(pitch, count, **kwargs)
						values['pitches'].append(p)

						if pitch.attributes['type'].value == 'B':
							balls = balls + 1
						elif pitch.attributes['type'].value == 'S':
							strikes = strikes + 1

					inning.append(values)
				self.append(inning)
				inning_num += 1
