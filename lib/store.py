from . import *
import MySQLdb

class Store:
	def __init__(self):
		self.db = MySQLdb.connect(host="localhost", read_default_file=CONSTANTS.CNF, db=CONSTANTS.DATABASE)
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