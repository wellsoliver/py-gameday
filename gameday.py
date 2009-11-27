#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from lib import game, atbats, hitchart, players, CONSTANTS, fetch, store
from sys import argv
from getopt import getopt
import logging

def usage():
	print argv[0], \
		'--year=XXXX', \
		'\n\n', \
		'optional: --month=x,y --day=x,y --type=[mlb, aaa, aa]'
	raise SystemExit

def getMonths(year):
	months = []

	url = '%syear_%4d/' % (CONSTANTS.BASE, year)
	soup = BeautifulSoup(fetch(url))
	for link in soup.findAll('a'):
		if link['href'].find('month') >= 0:
			month = int(link['href'].replace('month_', '').rstrip('/'))
			months.append(month)

	return months

def getDays(year, month):
	days = []
	
	url = '%syear_%4d/month_%02d/' % (CONSTANTS.BASE, year, month)
	soup = BeautifulSoup(fetch(url))
	for link in soup.findAll('a'):
		if link['href'].find('day') >= 0:
			day = int(link['href'].replace('day_', '').rstrip('/'))
			days.append(day)

	return days

if __name__ == '__main__':
	TYPE = 'mlb'
	YEAR = None
	MONTH = None
	DAY = None
	VERBOSE = False
	log = logging.getLogger('lib')
	
	try:
		opts, args = getopt(argv[1:], '', ['verbose', 'delta', 'year=', 'month=', 'day=', 'type='])
	except:
		usage()

	for opt, arg in opts:
		if opt == '--verbose':
			VERBOSE = True
		elif opt == '--year':
			YEAR = int(arg)
		elif opt == '--month':
			try:
				MONTH = [int(x) for x in arg.split(',')]
			except:
				usage()
		elif opt == '--day':
			try:
				DAY = [int(x) for x in arg.split(',')]
			except:
				usage()
		elif opt == '--type':
			if arg not in ['mlb', 'aaa']:
				usage()
			TYPE = arg
		
	if YEAR is None:
		usage()
		
	if VERBOSE:
		log.setLevel(logging.DEBUG)
		log.addHandler(logging.StreamHandler())
	else:
		log.setLevel(logging.ERROR)
		log.addHandler(logging.StreamHandler())
	
	#CONSTANTS.BASE = CONSTANTS.BASE + '%s/' % TYPE
	
	url = '%syear_%4d/' % (CONSTANTS.BASE, YEAR)
	soup = BeautifulSoup(fetch(url))

	if MONTH is None:
		months = getMonths(YEAR)
	else:
		months = MONTH
	
	for month in months:
		if DAY is None:
			days = getDays(YEAR, month)
		else:
			days = DAY
			
		month_url = '%smonth_%02d' % (url, month)
		month_soup = BeautifulSoup(fetch(month_url))

		for day in days:
			day_url = '%s/day_%02d' % (month_url, day)
			day_soup = BeautifulSoup(fetch(day_url))

			for game_link in day_soup.findAll('a'):
				if game_link['href'].find('gid_') >= 0:
					game_id = game_link['href'].rstrip('/')

					g = game.Game(game_id)
					g.save()

					ab = atbats.AtBats(game_id)
					ab.save()
					
					hitchart = hitchart.HitChart(game_id)
					hitchart.save()
					
					batters = players.Batters(game_id)
					batters.save()

					pitchers = players.Pitchers(game_id)
					pitchers.save()

			# update last after a day
			sql = 'DELETE FROM last;'
			store.query(sql, None)
			
			sql = 'INSERT INTO last (year, month, day) VALUES(%s, %s, %s)'
			store.query(sql, [YEAR, month, day])
			store.save()

	store.finish()