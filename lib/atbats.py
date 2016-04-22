from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from re import search
from . import *

class Pitch:
    def __init__(self, element, count, **kwargs):

        values = {}
        values['num'] = kwargs['num'] if 'num' in kwargs else None
        values['game_id'] = kwargs['game_id'] if 'game_id' in kwargs else None
        values['pitcher'] = kwargs['pitcher'] if 'pitcher' in kwargs else None
        values['batter'] = kwargs['batter'] if 'batter' in kwargs else None
        values['b'] = count['balls']
        values['s'] = count['strikes']

        # these change a lot :(
        # tired of taking them from the XML element
        # because maybe I don't have them in the schema
        FIELDS = ['des','id','type','x','y','on_1b','on_2b','on_3b','sv_id','start_speed',
            'end_speed','sz_top','sz_bot','pfx_x','pfx_z','px','pz','x0','y0','z0','vx0','vy0','vz0',
            'ax','ay','az','break_y','break_angle','break_length','pitch_type','type_confidence',
            'spin_dir','spin_rate','zone']

        for key in element.attributes.keys():
            if key in FIELDS:
                values[key] = element.attributes[key].value

        self.values = values

    def save(self):
        DB = store.Store()

        sql = 'REPLACE INTO pitch (%s) VALUES(%s)' % (','.join(self.values.keys()), ','.join(['%s'] * len(self.values)))
        DB.query(sql, self.values.values())
        DB.save()


class Runner:
    def __init__(self, element, **kwargs):
        self.values = kwargs

    def save(self):
        DB = store.Store()

        sql = 'REPLACE INTO runner (%s) VALUES(%s)' % (','.join(self.values.keys()), ','.join(['%s'] * len(self.values)))
        DB.query(sql, self.values.values())
        DB.save()


class AtBats(list):

    def save(self):
        DB = store.Store()
        for inning in self:
            for atbat in inning:
                keys = [k for k in atbat.keys() if k not in ('pitches',
                                                             'runners')]
                values = [None if atbat[k] == '' else atbat[k] for k in keys]

                sql ='REPLACE INTO atbat (%s) VALUES(%s)' % (','.join(keys), ','.join(['%s'] * len(keys)))
                DB.query(sql, values)
                DB.save()

                for pitch in atbat['pitches']:
                    pitch.save()

                for runner in atbat['runners']:
                    runner.save()

    def __init__(self, gid, game_id):
        super(AtBats,self).__init__()

        year, month, day = gid.split('_')[1:4]
        url = '%syear_%s/month_%s/day_%s/%s/inning/' % (CONSTANTS.BASE, year, month, day, gid)

        contents = Fetcher.fetch(url)
        if contents is None:
            return

        soup = BeautifulSoup(contents)

        inning_num = 1
        for inning_link in soup.findAll('a'):
            if search(r'inning_\d+\.xml', inning_link['href']):
                inning_url = '%s%s' % (url, inning_link['href'])
                doc = minidom.parseString(Fetcher.fetch(inning_url))

                inning = []
                # keep track of pitchers by runner on base for the inning
                pitchers_credited = {}
                for atbat in doc.getElementsByTagName('atbat'):
                    values = {}
                    half = atbat.parentNode.nodeName
                    for key in atbat.attributes.keys():
                        values[str(key)] = atbat.attributes[key].value

                    values['half'] = half
                    values['game_id'] = game_id
                    values['inning'] = inning_num
                    values['pitches'] = []
                    values['runners'] = []

                    batter = atbat.attributes['batter'].value
                    pitcher = atbat.attributes['pitcher'].value

                    balls = 0
                    strikes = 0
                    for pitch in atbat.getElementsByTagName('pitch'):
                        count = {'balls': balls, 'strikes': strikes}
                        kwargs = {'game_id': game_id,
                            'batter': values['batter'],
                            'pitcher': values['pitcher'],
                            'num': atbat.attributes['num'].value}
                        p = Pitch(pitch, count, **kwargs)
                        values['pitches'].append(p)

                        if pitch.attributes['type'].value == 'B':
                            balls = balls + 1
                        elif pitch.attributes['type'].value == 'S':
                            strikes = strikes + 1

                    values, pitchers_credited = self._parse_runners(atbat, values, pitchers_credited)

                    inning.append(values)

                self.append(inning)
                inning_num += 1


    def _parse_runners(self, atbat, values, pitchers_credited):
        for runner in atbat.getElementsByTagName('runner'):
            runner_attr = {
                'game_id': values['game_id'],
                'atbat': atbat.attributes['num'].value,
                'runner': runner.attributes['id'].value,
                'start_base': runner.attributes['start'].value,
                'end_base': runner.attributes['end'].value,
                'event': runner.attributes['event'].value,
                # Default pitcher is the one for this atbat
                'pitcher_credited': values['pitcher']
            }
            runner_id = runner.attributes['id'].value

            if runner_id == values['batter']:
                # The runner was the batter, so keep track of the pitcher
                # who put him on base
                pitchers_credited[runner_id] = values['pitcher']
            else:
                # In all other cases, use the original pitcher for this batter.
                #
                # TODO:
                # If a pinch runner was added this will not be set correctly.
                # Pinch runners will not be credited to the original
                # pitcher because the <action> tag for offensive substitutions
                # doesn't specify the player leaving without parsing the
                # `des` attribute and we don't parse the <action/> tag now.
                # Workaround is to default to the pitcher for the atbat
                runner_attr['pitcher_credited'] = pitchers_credited.get(runner_id, values['pitcher'])

            if runner.attributes['end'].value == '':
                # The runner scored or was put out, so remove him
                # because it is possible to be on base twice in an inning
                try:
                    del pitchers_credited[runner_id]
                except:
                    pass


            for attr in ('score', 'rbi', 'earned'):
                try:
                    if runner.attributes[attr].value == 'T':
                        runner_attr[attr] = 1
                except:
                    pass

            r = Runner(runner, **runner_attr)
            values['runners'].append(r)

        return values, pitchers_credited
