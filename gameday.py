#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from lib import game, atbats, hitchart, players, store, CONSTANTS, Fetcher
from sys import argv
from getopt import getopt
from time import strptime
import threading
import logging
import datetime
import MySQLdb
from ConfigParser import ConfigParser

def usage():
	print argv[0], \
		'--year=XXXX', \
		'\n\n', \
		'optional: --month=x,y --day=x,y --type=[mlb, aaa] --delta --verbose'
	raise SystemExit

def getMonths(year, start = 1):
	months = []

	url = '%syear_%4d/' % (CONSTANTS.BASE, year)
	soup = BeautifulSoup(Fetcher.fetch(url))
	for link in soup.findAll('a'):
		if link['href'].find('month') >= 0:
			month = int(link['href'].replace('month_', '').rstrip('/'))
			if month >= start:
				months.append(month)

	return months

def getDays(year, month, start = 1):
	days = []
	
	url = '%syear_%4d/month_%02d/' % (CONSTANTS.BASE, year, month)
	soup = BeautifulSoup(Fetcher.fetch(url))
	for link in soup.findAll('a'):
		if link['href'].find('day') >= 0:
			try:
				day = int(link['href'].replace('day_', '').rstrip('/'))
			except:
				# sometimes gameday will have like a '26_bak' directory
				continue
			if day >= start:
				days.append(day)

	return days

class Handler(threading.Thread):
	def __init__(self, url):
		threading.Thread.__init__(self)
		self.url = url

	def run(self):
		DB = store.Store()
		soup = BeautifulSoup(Fetcher.fetch(self.url))

		for link in soup.findAll('a'):
			if link['href'].find('gid_') >= 0:
				gid = link['href'].rstrip('/')
				
				g = game.Game(gid)
				g.save()
				game_id = g.game_id

				ab = atbats.AtBats(gid, game_id)
				ab.save()
				
				chart = hitchart.HitChart(gid, game_id)
				chart.save()
				
				batters = players.Batters(gid, game_id)
				batters.save()

				pitchers = players.Pitchers(gid, game_id)
				pitchers.save()

if __name__ == '__main__':
	TYPE = 'mlb'
	YEAR = None
	MONTH = None
	DAY = None
	VERBOSE = False
	DELTA = False
	log = logging.getLogger('gameday')
	startday = 1
	startmonth = 1

	# here lies a hack for the strptime thread bug
	foo = strptime('30 Nov 00', '%d %b %y')
	
	try:
		DB = store.Store()
	except MySQLdb.Error, e:
		print 'Database connection problem- did you setup a db.ini? (error: %s)' % e
		raise SystemExit
	
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
		elif opt == '--delta':
			DELTA = True
			sql = 'SELECT year, month, day FROM last WHERE type = %s'
			res = DB.query(sql, [TYPE])
			if len(res) == 0:
				print 'sorry, no delta information found'
				raise SystemExit
			else:
				YEAR, startmonth, startday = [int(x) for x in res[0]]

	if YEAR is None:
		usage()
		
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s')

	if VERBOSE:
		log.setLevel(logging.DEBUG)
		log.addHandler(logging.StreamHandler())
	else:
		log.setLevel(logging.ERROR)
		log.addHandler(logging.StreamHandler())
	
	logfilename = './log.txt'
	filelog = logging.FileHandler(logfilename, 'a')
	filelog.setLevel(logging.ERROR)
	filelog.setFormatter(formatter)
	
	log.addHandler(filelog)
	
	CONSTANTS.BASE = CONSTANTS.BASE.replace('%TYPE%', TYPE)
	url = '%syear_%4d/' % (CONSTANTS.BASE, YEAR)
	try:
		soup = BeautifulSoup(Fetcher.fetch(url))
	except TypeError, e:
		print 'Could not fetch %s' % url
		raise SystemExit

	if MONTH is None:
		if startmonth:
			months = getMonths(YEAR, startmonth)
		else:
			months = getMonths(YEAR)
	else:
		months = MONTH

	for month in months:
		if DAY is None:
			if startday:
				days = getDays(YEAR, month, startday)
			else:	
				days = getDays(YEAR, month)
		else:
			days = DAY
		
		month_url = '%smonth_%02d' % (url, month)
		month_soup = BeautifulSoup(Fetcher.fetch(month_url))

		threads = []
		for day in days:
			day_url = '%s/day_%02d' % (month_url, day)
			
			handler = Handler(day_url)
			handler.start()
			threads.append(handler)
			
		for thread in threads:
			thread.join()
			
		# update last after a day
		sql = 'DELETE FROM last WHERE type = %s;'
		DB.query(sql, [TYPE])
		
		sql = 'INSERT INTO last (type, year, month, day) VALUES(%s, %s, %s, %s)'
		DB.query(sql, [TYPE, YEAR, month, days[-1]])
		DB.save()

	DB.finish()
