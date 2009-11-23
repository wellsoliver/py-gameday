#!/usr/bin/env python
import threading
import xml.dom.minidom
import urllib
import BeautifulSoup
import MySQLdb
import time

TYPE = 'mlb'
YEAR = 2009
BASE = 'http://gd2.mlb.com/components/game/%s/' % TYPE
CNF='/home/wells/.my.cnf'
DATABASE='gameday'

db = MySQLdb.connect(host="localhost", read_default_file=CNF, db=DATABASE)
cursor = db.cursor()
url = '%syear_%4d/month_%02d/' % (BASE, YEAR, 5)
soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(url).read())

for link in soup.findAll('a'):
	if link['href'].find('day') >= 0:
		day_url = '%s%s' % (url, link['href'])
		day_soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(day_url).read())

		for game_link in day_soup.findAll('a'):
			if game_link['href'].find('gid_') >= 0:
				game_url = '%s%s' % (day_url, game_link['href'])
				game_soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(game_url).read())
				
				linescore = '%slinescore.xml' % game_url
				boxscore_url = '%sboxscore.xml' % game_url

				box = xml.dom.minidom.parseString(urllib.urlopen(boxscore_url).read()).getElementsByTagName('boxscore').item(0)

				game_id = box.attributes['game_id'].value
				home = box.attributes['home_fname'].value;
				away = box.attributes['away_fname'].value;
				date = time.strptime(box.attributes['date'].value, '%B %d %y')

				print game_id, home, away, date
				sql = 'INSERT INTO game (game_id, home, away, date) VALUES(%s)' % (','.join(['%s'] * 4))
				cursor.execute(sql, [game_id, home, away, date])
				db.commit()
				db.close()
				
				raise SystemExit