#!/usr/bin/env python
import threading
import xml.dom.minidom
import libxml2
import urllib
from BeautifulSoup import BeautifulSoup
import MySQLdb
import time
import re

TYPE = 'mlb'
YEAR = 2009
BASE = 'http://gd2.mlb.com/components/game/%s/' % TYPE
CNF='/home/wells/.my.cnf'
DATABASE='gameday'

class Game:
	FIELDS = ['game_id', 'game_pk', 'home_sport_code', 'home_team_code', 'home_id', 'home_fname', 'home_sname', 'home_wins', \
		'home_loss', 'away_team_code', 'away_id', 'away_fname', 'away_sname', 'away_wins', 'away_loss', 'status_ind', 'date']

	def _parseBox(self, elem):
		for key in elem.attributes.keys():
			if key in Game.FIELDS:
				val = elem.attributes[key].value

				if key == 'date':
					val = MySQLdb.DateFromTicks(time.mktime(time.strptime(val, '%B %d, %Y')))
				elif val.isdigit():
					val = int(val)
				else:
					val = str(val)
				
				setattr(self, key, val)

	def save(self):
		if self.status_ind == 'F':
			sql = 'INSERT INTO game (%s) VALUES(%s)' % (','.join(Game.FIELDS), ','.join(['%s'] * len(Game.FIELDS)))
			cursor.execute(sql, [getattr(self, field) for field in Game.FIELDS])
			db.commit()
			
			for inning in self.innings:
				for atbat in inning:
					sql = 'INSERT INTO atbat (%s) VALUES(%s)' % (','.join(atbat.keys()), ','.join(['%s'] * len(atbat.keys())))
					cursor.execute(sql, atbat.values())
				db.commit()
					

	def __init__(self, href):
		self.game_id = href.rstrip('/')
		self.innings = []
		
		_info = self.game_id.split('_')
		url = '%syear_%4d/month_%02d/day_%02d/%s/' % (BASE, int(_info[1]), int(_info[2]), int(_info[3]), self.game_id)
		soup = BeautifulSoup(fetch(url))

		box_url = '%sboxscore.xml' % url
		contents = fetch(box_url)
		
		if contents is not None:
			doc = xml.dom.minidom.parseString(contents)
			if doc.getElementsByTagName('boxscore').length == 1:
				self._parseBox(doc.getElementsByTagName('boxscore').item(0))
		
				innings_url = '%sinning/' % url
				soup = BeautifulSoup(fetch(innings_url))
		
				inning = 0
				for inning_link in soup.findAll('a'):
					if re.search(r'inning_\d+\.xml', inning_link['href']):
						inning_url = '%s%s' % (innings_url, inning_link['href'])
						doc = xml.dom.minidom.parseString(fetch(inning_url))
						self.innings.append([])
				
						values = {}
						for atbat in doc.getElementsByTagName('atbat'):
							half = atbat.parentNode.nodeName
							for key in atbat.attributes.keys():
								values[str(key)] = atbat.attributes[key].value
							values['half'] = half
							values['game_id'] = self.game_id
							values['inning'] = inning + 1
					
							self.innings[inning].append(values)
						inning += 1	

				self.save()

def fetch(url):
	for i in xrange(10):
		#print 'fetching %s (%d)' % (url, i)
		try:
			page = urllib.urlopen(url)
		except IOError:
			time.sleep(1)
			continue

		if page.getcode() == 404:
			return None
		else:
			return page.read()
		break

db = MySQLdb.connect(host="localhost", read_default_file=CNF, db=DATABASE)
cursor = db.cursor()
url = '%syear_%4d/month_%02d/' % (BASE, YEAR, 5)
soup = BeautifulSoup(fetch(url))

for link in soup.findAll('a'):
	if link['href'].find('day') >= 0:
		day_url = '%s%s' % (url, link['href'])
		day_soup = BeautifulSoup(fetch(day_url))

		for game_link in day_soup.findAll('a'):
			if game_link['href'].find('gid_') >= 0:
				game = Game(game_link['href'])

db.close()