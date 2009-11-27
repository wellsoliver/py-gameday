from MySQLdb import connect
from logging import getLogger, Handler
from urllib import urlopen
from warnings import simplefilter
from time import sleep

import MySQLdb

class NullHandler(Handler):
	def emit(self, record):
		pass

class CONSTANTS:
	BASE = 'http://gd2.mlb.com/components/game/mlb/'
	CNF='/home/wells/.my.cnf'
	DATABASE='gameday'

def fetch(url):
	for i in xrange(10):
		logger.debug('FETCH %s' % url)
		try:
			page = urlopen(url)
		except IOError:
			time.sleep(1)
			continue

		sleep(.5)
		if page.getcode() == 404:
			return None
		else:
			return page.read()
		break

class Store:
	def __init__(self):
		self.db = connect(host="localhost", read_default_file=CONSTANTS.CNF, db=CONSTANTS.DATABASE)
		self.cursor = self.db.cursor()
		
	def save(self):
		self.db.commit()
	
	def finish(self):
		self.db.commit()
		self.db.close()
		
	def query(self, query, values):
		simplefilter("error", MySQLdb.Warning)
		
		try:
			self.cursor.execute(query, values)
		except MySQLdb.Error, e:
			logger.error(e)
		except MySQLdb.Warning, e:
			logger.error(e)
			
store = Store()
logger = getLogger(__name__)
logger.addHandler(NullHandler())