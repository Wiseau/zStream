import datetime
import math
import time

import esi


class Victim:
    def __init__(self, v):
        self.raw = v
        self.ship = self.ship()
        self.alliance = self.alliance()

    def alliance(self):
        if 'alliance_id' in self.raw:
            self.alliance = esi.get_alliance(self.raw['alliance_id'])
            return self.alliance
        else:
            return None

    def ship(self):
        self.ship = esi.get_type(self.raw['ship_type_id'])
        return self.ship

    def __getattr__(self, item):
        setattr(self, item, self.raw[item])
        return getattr(self, item, self.raw[item])


class Killmail:
    def __init__(self, k):
        self.raw = k
        self.value = k['zkb']['totalValue']
        self.id = k['killmail_id']
        self.is_solo = k['zkb']['solo']
        self.is_awox = k['zkb']['awox']
        self.is_npc = k['zkb']['npc']
        self.is_cyno = self.is_cyno()

        self.victim = Victim(k['victim'])
        self.system = esi.get_solar_system(k['solar_system_id'])

    def __getattr__(self, item):
        setattr(self, item, self.raw[item])
        return getattr(self, item, self.raw[item])

    def is_cyno(self):
        self.is_cyno = False
        for item in self.raw['victim']['items']:
            if item['item_type_id'] is 21096 and item['flag'] in range(27, 35):
                self.is_cyno = True
        return self.is_cyno

    def get_value_millified(self, places=0):
        millnames = ['', 'k', 'm', 'b', 't']
        n = float(self.value)
        millidx = max(0, min(len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

        return '{0:.{2}f}{1}'.format(n / 10 ** (3 * millidx), millnames[millidx], places)

    def diff_in_seconds(self):
        kill_time = int(datetime.datetime.strptime(self.raw['killmail_time'], "%Y-%m-%dT%H:%M:%SZ").timestamp())
        now = int(time.time())
        return datetime.timedelta(seconds=(now - 3600) - kill_time)
