import discord
from utilities import card_info as uc


# Full custom message
def format_msg(title, color, desc='', url=''):
    return discord.Embed(title=title, color=color, description=desc, url=url)


# Confirm message
def confirm_msg(title, desc=''):
    return discord.Embed(title=title, description=desc, color=discord.Color.dark_green())


# Error message
def err_msg(title, desc=''):
    return discord.Embed(title=title, description=desc, color=discord.Color.dark_red())


# Info message
def info_msg(title, desc=''):
    return discord.Embed(title=title, description=desc, color=discord.Color.dark_gold())


# Multiple cards message
def multi_msg(card_id, emojis):
    card_names = [uc.extract_info(i)['name'] for i in card_id]
    msg_desc = ''

    for i in range(len(card_names)):
        msg_desc += f'{emojis[i]} {card_names[i]}\n'
    msg_desc += f'\nPlease react to the emoji of the card you wish to see'

    return discord.Embed(
        title=f'More than one card found:',
        description=f'{msg_desc}',
        color=discord.Color.random()
    )
