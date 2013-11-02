from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from MySQLdb import DateFromTicks
from time import mktime, strptime
from . import CONSTANTS, store, Fetcher

class Game:
	FIELDS = ['game_id', 'game_type', 'local_game_time', 'game_pk', 'game_time_et', 'home_sport_code', 'home_team_code', 'home_id', \
	'home_fname', 'home_sname', 'home_wins', 'home_loss', 'away_team_code', 'away_id', 'away_fname', 'away_sname', 'away_wins', \
	'away_loss', 'status_ind', 'date', 'day','stadium_id', 'stadium_name', 'stadium_location']

	def _parseBox(self, elem):
		for key in elem.attributes.keys():
			if key in Game.FIELDS:
				val = elem.attributes[key].value

				if key == 'date':
					val = DateFromTicks(mktime(strptime(val, '%B %d, %Y')))
				elif val.isdigit():
					val = int(val)
				else:
					val = str(val)
				
				setattr(self, key, val)

	def save(self):
		# make sure we have a status, said status is F(inal), and
		# that we have a game_type
		if self.status_ind and \
			self.game_type and \
			self.status_ind == 'F':
			DB = store.Store()
			sql = 'REPLACE INTO game (%s) VALUES(%s)' % (','.join(Game.FIELDS), ','.join(['%s'] * len(Game.FIELDS)))
			DB.query(sql, [getattr(self, field) for field in Game.FIELDS])
			DB.save()

	def __init__(self, game_id):
		self.game_id = game_id
		self.status_ind = self.game_type = None

		year, month, day = game_id.split('_')[1:4]
		url = '%syear_%s/month_%s/day_%s/%s/' % (CONSTANTS.BASE, year, month, day, game_id)
		soup = BeautifulSoup(Fetcher.fetch(url))
		
		game_url = '%sgame.xml' % url
		game_contents = Fetcher.fetch(game_url)

		box_url = '%sboxscore.xml' % url
		contents = Fetcher.fetch(box_url)
		
		linescore_url = '%slinescore.xml' % url
		linescore_contents = Fetcher.fetch(linescore_url)
		
		if contents is not None and linescore_contents is not None and game_contents is not None:
			doc = minidom.parseString(contents)
			line = minidom.parseString(linescore_contents)
			game_general = minidom.parseString(game_contents)
			
			if game_general.getElementsByTagName('game').length==1:
				game = game_general.getElementsByTagName('game').item(0)
				self.local_game_time = game.attributes['local_game_time'].value
				self.game_time_et = game.attributes['game_time_et'].value
			
			if game_general.getElementsByTagName('stadium').length==1:
				stadium = game_general.getElementsByTagName('stadium').item(0)
				self.stadium_id = stadium.attributes['id'].value
				self.stadium_name = stadium.attributes['name'].value
				self.stadium_location = stadium.attributes['location'].value
			
			if line.getElementsByTagName('game').length == 1:
				game = line.getElementsByTagName('game').item(0)
				self.game_type = game.attributes['game_type'].value
				self.day = game.attributes['day'].value

			if doc.getElementsByTagName('boxscore').length == 1:
				self._parseBox(doc.getElementsByTagName('boxscore').item(0))