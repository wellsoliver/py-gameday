from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from MySQLdb import DateFromTicks
from time import mktime, strptime
from . import *

class Game:
	FIELDS = ['game_id', 'game_type', 'game_pk', 'home_sport_code', 'home_team_code', 'home_id', 'home_fname', 'home_sname', 'home_wins', \
		'home_loss', 'away_team_code', 'away_id', 'away_fname', 'away_sname', 'away_wins', 'away_loss', 'status_ind', 'date']

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
			sql = 'REPLACE INTO game (%s) VALUES(%s)' % (','.join(Game.FIELDS), ','.join(['%s'] * len(Game.FIELDS)))
			store.query(sql, [getattr(self, field) for field in Game.FIELDS])
			store.save()

	def __init__(self, game_id):
		self.game_id = game_id
		self.status_ind = self.game_type = None

		year, month, day = game_id.split('_')[1:4]
		url = '%syear_%s/month_%s/day_%s/%s/' % (CONSTANTS.BASE, year, month, day, game_id)
		try:
			soup = BeautifulSoup(fetch(url))
		except:
			print 'error processing %s' % url
			return

		box_url = '%sboxscore.xml' % url
		contents = fetch(box_url)
		
		linescore_url = '%slinescore.xml' % url
		linescore_contents = fetch(linescore_url)
		
		if contents is not None and linescore_contents is not None:
			doc = minidom.parseString(contents)
			line = minidom.parseString(linescore_contents)

			if line.getElementsByTagName('game').length == 1:
				game = line.getElementsByTagName('game').item(0)
				self.game_type = game.attributes['game_type'].value

			if doc.getElementsByTagName('boxscore').length == 1:
				self._parseBox(doc.getElementsByTagName('boxscore').item(0))