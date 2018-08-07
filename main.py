import sys
import config
import esi
import logging
from discord_webhook import DiscordHook
from arceus import Arceus
from zsocket import ZSocket

logger = logging.getLogger("zStream")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

Arceus = Arceus()
socket = ZSocket()


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


def decourate_discord(killmail):
    hook = DiscordHook()
    hook.url = "https://zkillboard.com/kill/%s/" % killmail.id
    hook.color = 275725
    hook.timestamp = killmail.killmail_time
    hook.set_footer(text="zStream", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    hook.set_thumbnail(url="https://image.eveonline.com/Type/%s_64.png" % killmail.victim.ship.id)
    hook.set_author(name="%s in %s" % (killmail.victim.ship.name, killmail.system.name),
                    url="https://zkillboard.com/kill/%s/" % killmail.id)

    if killmail.victim.alliance:
        hook.add_field(name="Alliance", description=killmail.victim.alliance.name, inline=True)

    hook.add_field(name="Attackers", description=str(len(killmail.attackers)), inline=True)
    hook.add_field(name="Price", description=killmail.get_value_millified(2), inline=True)
    hook.add_field(name="Time Ago", description=str(killmail.diff_in_seconds()), inline=True)

    description = []
    if killmail.is_cyno:
        description.append("CYNO")
    if killmail.value > 1000000000:
        description.append("Expensive")
    if killmail.is_npc is True:
        description.append("NPC")
    if killmail.is_awox is True:
        description.append("AWOX")
    if killmail.is_solo is True:
        description.append("SOLO")
    if description:
        hook.description = ', '.join(description)

    return hook


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
    if killmail.is_cyno:
        decoration += " CYNO"
    if killmail.value > 1000000000:
        decoration += " $$$"

    return decoration


def rules(killmail):
    rules = []
    if killmail.victim.ship.id in config.group_short_names:
        if config.group_short_names[killmail.victim.ship.id] in ["TIT", "SPR"]:
            rules.append("super")

    if killmail.value > 1000000000:
        rules.append("expensive")

    return rules


def on_open(ws):
    Arceus.privmsg(config.channel, "zStream starting...")


def on_error(ws, err):
    Arceus.privmsg(config.channel, "zStream failed with error: %s" % err)


def on_killmail(ws, killmail):
    logger.info("Received kill %s from websocket" % killmail.id)

    rule = rules(killmail)
    irc_content = decorate_irc(killmail)
    if "super" in rule:
        Arceus.notice(config.channel, irc_content)
        Arceus.privmsg(config.channel_important, irc_content)
        for webhook in config.discord_webhooks_all:
            decourate_discord(killmail).send(webhook)
    else:
        Arceus.privmsg(config.channel, irc_content)
        for webhook in config.discord_webhooks_all:
            decourate_discord(killmail).send(webhook)

    if "expensive" in rule:
        for webhook in config.discord_webhooks_expensive:
            decourate_discord(killmail).send(webhook)


if __name__ == "__main__":
    try:
        logger.info("Starting zStream")
        populate_groups()
        socket.on_killmail = on_killmail
        socket.socket_open = on_open
        socket.socket_error = on_error
        socket.start()
    except KeyboardInterrupt:
        sys.exit(0)
    pass
