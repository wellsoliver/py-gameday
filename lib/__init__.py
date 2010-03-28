from logging import getLogger, Handler
from urllib import urlopen
from warnings import simplefilter
from time import sleep

class NullHandler(Handler):
	def emit(self, record):
		pass

class CONSTANTS:
	BASE = 'http://gd2.mlb.com/components/game/%TYPE%/'

class Fetcher:
	@classmethod
	def fetch(self, url):
		for i in xrange(10):
			logger.debug('FETCH %s' % url)
			try:
				page = urlopen(url)
			except IOError, e:
				logger.error('ERROR %s' % url)
				sleep(1)
				continue

			sleep(.5)
			if page.getcode() == 404:
				return None
			else:
				return page.read()
			break

logger = getLogger('gameday')
logger.addHandler(NullHandler())
