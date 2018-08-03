import sys
import config
import esi
import logging
from arceus import Arceus
import zsocket

logger = logging.getLogger("zStream")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

Arceus = Arceus()
socket = zsocket.zsocket()


def populate_groups():
    logging.info("Getting ship categories from ESI")
    categories = esi.get("universe/categories/%s" % 6)
    for group_id in categories['groups']:
        group = esi.get("universe/groups/%s" % group_id)
        for type_id in group['types']:
            esi.ship_group_name[type_id] = group['name']
            if group['name'] in config.group_short_names:
                esi.ship_group_name[type_id] = config.group_short_names[group['name']]
            else:
                esi.ship_group_name[type_id] = group['name']

    logging.info("Finished getting ship categories from ESI total ship types: %s" % len(esi.ship_group_name))


def decorate_irc(killmail):
    decoration = "\x02\x0304%s\x03\x02" % killmail.victim.ship.name
    if killmail.victim.alliance:
        decoration += " [%s]" % killmail.victim.alliance.ticker
    decoration += " in \x02\x0310%s\x03\x02" % killmail.system.name
    decoration += " A:\x02%s\x02" % len(killmail.attackers)
    decoration += " T:\x02%s\x02" % killmail.diff_in_seconds()
    decoration += " P:\x02%s\x02" % killmail.get_value_millified(2)
    decoration += " https://zkillboard.com/kill/%s/" % killmail.id
    if killmail.is_npc is True:
        decoration += " [NPC]"
    if killmail.is_awox is True:
        decoration += " [AWOX]"
    if killmail.is_solo is True:
        decoration += " [SOLO]"
    if killmail.victim.ship.id in esi.ship_group_name:
        group_name = esi.ship_group_name[killmail.victim.ship.id]
        if group_name in config.group_colours:
            group_colour = config.group_colours[group_name]
            decoration += " \x03%s%s\x03" % (group_colour, group_name)
        else:
            decoration += " %s" % group_name
    if killmail.value > 1000000000:
        decoration += " $$$"

    return decoration


def rules(killmail):
    if killmail.victim.ship.id in config.group_short_names:
        if config.group_short_names[killmail.victim.ship.id] in ["TIT", "SPR"]:
            return "super"

    return None


def on_open(ws):
    Arceus.privmsg(config.channel, "zStream starting...")


def on_error(ws, err):
    Arceus.privmsg(config.channel, "zStream connection failed with error: %s" % err)


def on_killmail(ws, killmail):
    logger.info("Received kill %s from websocket" % killmail.id)

    rule = rules(killmail)
    if rule is "super":
        Arceus.notice(config.channel, decorate_irc(killmail))
        Arceus.privmsg(config.channel_important, decorate_irc(killmail))
    else:
        Arceus.privmsg(config.channel, decorate_irc(killmail))


if __name__ == "__main__":
    try:
        logger.info("Starting zStream")
        populate_groups()
        socket = zsocket.zSocket()
        socket.on_killmail = on_killmail
        socket.socket_open = on_open
        socket.socket_error = on_error
        socket.start()
    except KeyboardInterrupt:
        sys.exit(0)
    pass
