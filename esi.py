import requests
import json
import logging

esi_url = "https://esi.evetech.net/latest/"

s = requests.session()
ship_group_name = {}
alliances = {}
solar_systems = {}
types = {}

logger = logging.getLogger('ESI')


class System:
    def __init__(self, system_id):
        self.id = system_id

    def __getattr__(self, item):
        self.raw = get("universe/systems/%s/" % self.id)
        for key in self.raw.keys():
            setattr(self, key, self.raw[key])
        return getattr(self, item)


class Type:
    def __init__(self, type_id):
        self.id = type_id

    def __getattr__(self, item):
        self.raw = get("universe/types/%s/" % self.id)
        for key in self.raw.keys():
            setattr(self, key, self.raw[key])
        return getattr(self, item)


class Alliance:
    def __init__(self, alliance_id):
        self.id = alliance_id

    def __getattr__(self, item):
        self.raw = get("alliances/%s/" % self.id)
        for key in self.raw.keys():
            setattr(self, key, self.raw[key])
        return getattr(self, item)


def fire(method, url, data):
    url = url.rstrip('/')
    url = esi_url + url
    headers = {'content-type': 'application/json'}
    r = s.request(method=method, url=url, data=json.dumps(data), headers=headers)
    logger.debug("%s(%s): %s - %s in %s" % (method, r.status_code, url, data, r.elapsed))
    return r.json()


def get(url, data=None):
    return fire('GET', url, data)


def post(url, data=None):
    return fire('POST', url, data)


def get_solar_system(system_id):
    if system_id in solar_systems:
        return solar_systems[system_id]
    else:
        solar_systems[system_id] = System(system_id)
        return solar_systems[system_id]


def get_alliance(alliance_id):
    if alliance_id in alliances:
        return alliances[alliance_id]
    else:
        alliances[alliance_id] = Alliance(alliance_id)
        return alliances[alliance_id]


def get_type(type_id):
    if type_id in types:
        return types[type_id]
    else:
        types[type_id] = Type(type_id)
        return types[type_id]
