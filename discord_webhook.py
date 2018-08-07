import logging
import requests
import json

logger = logging.getLogger('DiscordWebhook')


class DiscordHook:
    def __init__(self):
        self.color = None
        self.timestamp = None
        self.url = None
        self.type = None
        self.title = None
        self.description = None

        self.footer = None
        self.author = None
        self.thumbnail = None
        self.title = None

        self.fields = []

    def set_thumbnail(self, url: str, proxy_url: str = None, height: int = None, width: int = None):
        thumbnail = {'url': url}
        if proxy_url:
            thumbnail['proxy_url'] = proxy_url
        if height:
            thumbnail['height'] = height
        if width:
            thumbnail['width'] = width

        self.thumbnail = thumbnail

    def set_footer(self, text: str, icon_url: str = None, proxy_icon_url: str = None):
        footer = {"text": text}
        if icon_url:
            footer['icon_url'] = icon_url
        if proxy_icon_url:
            footer['proxy_icon_url'] = proxy_icon_url

    def set_author(self, name: str, url: str = None, icon_url=None, proxy_icon_url: str = None):
        author = {"name": name}
        if url:
            author['url'] = url
        if icon_url:
            author['icon_url'] = icon_url
        if proxy_icon_url:
            author['proxy_icon_url'] = proxy_icon_url

        self.author = author

    def add_field(self, name: str, description: str, inline: bool = False):
        self.fields.append({
            "name": name,
            "value": description,
            "inline": inline
        })

    def to_dict(self):
        j = self.__dict__
        for k, v in dict(j).items():
            if v is None:
                del j[k]
        return j

    def send(self, url):
        logger.debug("sending killmail to discord: %s" % url)
        headers = {'content-type': 'application/json'}
        r = requests.post(url=url,
                          data=json.dumps({'embeds': [self.to_dict()]}),
                          headers=headers)
        return r
