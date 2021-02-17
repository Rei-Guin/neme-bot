import requests
import re
import discord

from utilities import neme_msg as un
from utilities import arg_extract as ua


# Retrieve card ids using the link generated from get_link
def get_id(args):
    r = requests.get(get_link(args))

    # retrieve card id from shadowver-portal
    id_strings = []
    [id_strings.append(val) for val in re.findall('/card/[0-9]+', r.text) if val not in id_strings]
    ids = list(map(lambda val: val.split('/')[2], id_strings))

    return ids


# Generate shadowverse-portal link including arguments passed by user
def get_link(args):
    # all arguments for search URL
    opt_list = {
        'c': 'clan[]=',
        'f': 'format=',
        'p': 'card_set[]=',
        'm': 'cost[]=',
        't': 'char_type[]=',
        'r': 'rarity[]=',
        'n': 'card_name=',
        'k': 'card_text='
    }

    # this list marks the target arguments needed
    # so Neme can filter out the not needed arguments
    targets = []

    # Loop through all arguments, create needed arguments for shadowverse-portal link
    for i in range(len(args)):
        temp = ua.get_arg(args[i])

        if temp['opt'] in opt_list:
            targets.append(temp['opt'])
            opt_list[temp['opt']] += f'&{opt_list[temp["opt"]]}'.join(temp['val'])

    # filter out not needed arguments and change their value to ''
    for val in list(opt_list.keys()):
        if val not in targets:
            opt_list[val] = ''

    # Generate URL
    url = f'https://shadowverse-portal.com/cards?{opt_list["n"]}&{opt_list["c"]}&{opt_list["f"]}' \
          f'&{opt_list["p"]}&{opt_list["m"]}&{opt_list["t"]}&{opt_list["r"]}&{opt_list["k"]}&lang=en'

    # For debugging purpose
    print(url)
    return url


# Extract card info
def extract_info(card_id):
    r = requests.get(f'https://shadowverse-portal.com/card/{card_id}?lang=en')

    # Fill card details and return this info to format the card
    card_info = {
        'name': re.search(r'card-main-title">\r\n.*', r.text).group(0).split('\n')[1][:-1],
        'class': re.search(r'Class:\r\n</span>\r\n<span>\r\n.*', r.text).group(0).split('\n')[-1][:-1],
        'rarity': re.search(r'Rarity:\r\n</span>\r\n<span>\r\n.*', r.text).group(0).split('\n')[-1][:-1],
        'pack': re.search(r'Card Pack:\r\n</span>\r\n.*', r.text).group(0).split('\n')[-1][:-1],
        'attack': [val.split('\n')[-1] for val in re.findall(r'is-atk">\r\n\d+', r.text)],
        'life': [val.split('\n')[-1] for val in re.findall(r'is-life">\r\n\d+', r.text)],
        'effects': [val.split('\n')[1].replace('<br>', '\r\n')
                    for val in re.findall(r'card-content-skill">\r\n.*', r.text)]
    }

    return card_info


# Format card before sending
def format_card(card_info, card_id):
    # Main message for bot
    msg = un.format_msg(
        title=card_info['name'],
        url=f'https://shadowverse-portal.com/card/{card_id}?lang=en',
        desc=f'{card_info["class"]} {card_info["rarity"]}\r\nSet: {card_info["pack"]}',
        color=discord.Color.random()
    )

    # Card has attack and life, format as a follower
    if len(card_info['attack']) == 2 and len(card_info['life']) == 2:
        msg.add_field(name=f'**Unevolved: {card_info["attack"][0]}/{card_info["life"][0]}**',
                      value=f'{card_info["effects"][0]}', inline=False)
        msg.add_field(name=f'**Evolved: {card_info["attack"][0]}/{card_info["life"][0]}**',
                      value=f'{card_info["effects"][1]}', inline=False)

    # Else card is either spells or amulets
    else:
        msg.add_field(name=f'Effects: ', value=f'{card_info["effects"][0]}', inline=False)

    # Set image for formatted card
    msg.set_image(url=f'https://svgdb.me/assets/fullart/{card_id}0.png')

    return msg
