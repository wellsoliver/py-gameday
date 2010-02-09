from . import *
import MySQLdb
from ConfigParser import ConfigParser

class Store:
	def __init__(self, **args):
		parser = ConfigParser()
		parser.read('./db.ini')
		user = parser.get('db', 'user')
		password = parser.get('db', 'password')
		db = parser.get('db', 'db')
		
		args = {'user': user, 'passwd': password, 'db': db}

		if parser.has_option('db', 'host'):
			args['host'] = parser.get('db', 'host')
		
		self.db = MySQLdb.connect(**args)
		self.cursor = self.db.cursor()
		
	def save(self):
		self.db.commit()
	
	def finish(self):
		self.db.commit()
		self.db.close()
		
	def query(self, query, values = None):
		simplefilter("error", MySQLdb.Warning)
		
		try:
			res = self.cursor.execute(query, values)
		except MySQLdb.Error, e:
			logger.error('%s: %s' % (e, query))
		except MySQLdb.Warning, e:
			logger.error('%s: %s' % (e, query))
		
		return self.cursor.fetchall()