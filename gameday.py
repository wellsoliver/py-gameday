#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from lib import game, atbats, hitchart, players, store, CONSTANTS, Fetcher
import argparse
from time import strptime
import threading
import logging
import datetime
import MySQLdb
from ConfigParser import ConfigParser

def csv(value):
    ''' defines csv type for argparse add_argument() for month's & day's '''
    return map(int,value.split(','))


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
    def __init__(self, url, gametype):
        threading.Thread.__init__(self)
        self.url = url
        self.gametype = gametype

    def run(self):
        DB = store.Store()
        soup = BeautifulSoup(Fetcher.fetch(self.url))

        for link in soup.findAll('a'):
            if link['href'].find('gid_') >= 0:
                gid = link['href'].rstrip('/')
                
                g = game.Game(gid)
                if (g.game_type != self.gametype):
                    continue;

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

    ############ argparse stuff, to define & capture commandline options
    opt = argparse.ArgumentParser(prog="Py-Gameday",
                        description="Grabs MLB Gameday data",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                    

    opt.add_argument("-y","--year", default="2015", type=int,
                     required=True,
                     choices=range(2001,2016),
                     metavar='YYYY',
                     help="Required. 4 digit year.",)
    # optional arg's
    opt.add_argument("-m","--month", default="3", type=csv,
                     metavar='M,M',
                     help="1-2 digit month.",)
    opt.add_argument("-d","--day", 
                     default="1",
                     type=csv,
                     metavar='D,D',
                     help="1-2 digit day.",)
    opt.add_argument("-l","--league",
                     choices=['mlb','aaa','aax'],
                     default="mlb",
                     help="league abbreviation.",)
    opt.add_argument("-t","--gametype",
                     choices=['R', 'S', 'A', 'F', 'D', 'L', 'W'],
                     default="R",
                     help="R=regular season, S=spring training,\
                           A=allstar game, F=wildcard, D=division series,\
                           L=league series, W=world series.",)
    opt.add_argument('-v','--version', 
                     action='version', version='%(prog)s 1.0.1')
    opt.add_argument("-e","--errors",default="log.txt")
    opt.add_argument("-a","--delta",action="store_true")
    opt.add_argument("-b","--verbose",action="store_true")

    args = opt.parse_args()
    ############ end of the argparse details

    log = logging.getLogger('gameday')
    startday = 1
    startmonth = 1
    
    # here lies a hack for the strptime thread bug
    foo = strptime('30 Nov 00', '%d %b %y')
    
    # initial DB code
    try:
        DB = store.Store()
    except MySQLdb.Error, e:
        print 'Database connection problem- did you setup a db.ini? (error: %s)' % e
        raise SystemExit
    

    if args.delta:
        sql = 'SELECT year, month, day FROM last WHERE type = %s'
        res = DB.query(sql, [args.league])
        if len(res) == 0:
            print 'sorry, no delta information found'
            raise SystemExit
        else:
            args.year, startmonth, startday = [int(x) for x in res[0]]
    

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s')

    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler())
    else:
        log.setLevel(logging.ERROR)
        log.addHandler(logging.StreamHandler())
    
    logfilename = './' + args.errors
    filelog = logging.FileHandler(logfilename, 'a')
    filelog.setLevel(logging.ERROR)
    filelog.setFormatter(formatter)
    
    log.addHandler(filelog)
    
    CONSTANTS.BASE = CONSTANTS.BASE.replace('%LEAGUE%', args.league)
    url = '%syear_%4d/' % (CONSTANTS.BASE, args.year)
    try:
        soup = BeautifulSoup(Fetcher.fetch(url))
    except TypeError, e:
        print 'Could not fetch %s' % url
        raise SystemExit

    if args.month is None:
        if startmonth:
            months = getMonths(args.year, startmonth)
        else:
            months = getMonths(args.year)
    else:
        months = args.month

    for month in months:
        if args.day is None:
            if startday:
                days = getDays(args.year, month, startday)
            else:    
                days = getDays(args.year, month)
        else:
            days = args.day
        
        month_url = '%smonth_%02d' % (url, month)
        month_soup = BeautifulSoup(Fetcher.fetch(month_url))

        threads = []
        for day in days:
            day_url = '%s/day_%02d' % (month_url, day)
            
            handler = Handler(day_url, args.gametype)
            handler.start()
            threads.append(handler)
            
        for thread in threads:
            thread.join()
            
        # update last after a day
        sql = 'DELETE FROM last WHERE type = %s;'
        DB.query(sql, [args.league])
        
        sql = 'INSERT INTO last (type, year, month, day) VALUES(%s, %s, %s, %s)'
        DB.query(sql, [args.league, args.year, month, days[-1]])
        DB.save()

    DB.finish()

