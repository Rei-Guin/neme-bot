import asyncio
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from utilities import card_info as uc
from utilities import io_helper as uio
from utilities import arg_extract as ua
from utilities import neme_msg as un

from neme_exceptions.int_out_of_range import IntOutOfRange

# Load token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Prefix for Neme
bot = commands.Bot(command_prefix='.')


# Ready notification
@bot.event
async def on_ready():
    print('At your service!')


# Neme introduction
@bot.command()
async def neme(ctx):
    msg = un.format_msg(title=f'Hello, my name is Neme',
                        color=discord.Color.dark_blue())

    msg.add_field(name=f'Good to see you!! I hope you enjoy your stay',
                  value='I will help you to find cards and generate decks from codes. '
                        'Please use **".opts" for usage**')

    await ctx.send(embed=msg)


# Display Neme card and deck options
@bot.command()
async def opts(ctx):
    msg = un.format_msg(title=f'Neme Guideline',
                        color=discord.Color.dark_gold())

    msg.add_field(name=f'Card Search format: .c [option] [search keyword]',
                  value=f'If you want to assign **multiple values** for an option, **connect them with + sign**. '
                        f'Please note that if there are too many targets, Neme will not retrieve them all\n'
                        f'**c(class):** class of card **ranging from 0-7**, **0 being neutral** '
                        f'and **7 being Portal**, can assign **multiple values**\n'
                        f'**f(format):** assign **number 1** for **rotation** and '
                        f'**number 2** for **unlimited** format\n'
                        f'**p(pack):** assign **shorthands only**, type **.p** to retrieve **shorthand names**, '
                        f'can assign **multiple packs**\n'
                        f'**m(mana cost):** mana cost of card, can assign **multiple costs**\n'
                        f'**t(type):** type of card: **1(followers)**, **2(spells)**, **3(amulets)**, '
                        f'can assign **multiple values**\n'
                        f'**r(rarity):** rarity: **1(bronze)**, **2(silver)**, **3(gold)**, **4(legendary)**, '
                        f'can assign **multiple values**\n'
                        f'**n(name): card name**, can use **more than 1 word, connect with +**\n'
                        f'**k(keyword): card text**, can use **more than 1 word, connect with +**\n'
                        f'*Ex:* **.c c=5 p=fortune+eternal m=5 t=f+s r=l lover**\n',
                  inline=False)

    msg.add_field(name=f'Deck Search format: .d [option] [deck code]',
                  value=f'**Only one deck code at a time**\n'
                        f'**t(type):** **default** type is **image**, **assign** letter **l** for **link**\n'
                        f'*Ex:* **.d t=l a1cu**',
                  inline=False)

    await ctx.send(embed=msg)


# Retrieve pack shorthands for card search function
@bot.command()
async def p(ctx, p_format=''):
    # No arguments, display options for pack search function
    if p_format == '':
        msg = un.format_msg(title=f'Expansion shorthands',
                            color=discord.Color.dark_grey())
        msg.add_field(name=f'Pack display format: .p [option]',
                      value=f'**f(format):** **assign** number **1** for **rotation** format and '
                            f'**2** for **unlimited** format\n'
                            f'*Ex:* **.p f=0**')
        await ctx.send(embed=msg)
        return

    # if there are arguments
    # retrieve and split arguments
    args_dict = ua.get_arg(p_format)

    # Check for invalid inputs
    try:
        args_dict['val'] = [int(i) for i in args_dict['val']]
    except ValueError:
        await ctx.send(embed=un.err_msg(title='Value error', desc='Invalid number'))
        return

    # Check for out of range inputs
    try:
        if args_dict['val'][0] > 1:
            raise IntOutOfRange(args_dict['val'][0],
                                f'is **out of range**, please enter a number '
                                f'**between 1(rotation) and 2(unlimited)** only')
    except IntOutOfRange as e:
        await ctx.send(embed=un.err_msg(title='Value error', desc=f'{str(e)}'))
        return

    # Check for pack names file
    shorthands = uio.read('pack_info/sets.txt')
    if shorthands == 'file not found':
        await ctx.send(embed=un.err_msg(title='Internal error',
                                        desc=f'Error reading packs information, please contact developer of Neme'))
        return

    # Split the shorthands and replace spaces with empty strings
    content = [val.split(':')[1].replace(' ', '')
               for val in shorthands]

    # Rotation
    if args_dict['val'][0] == 1:
        msg_desc = ' - '.join(content[:5])

    # Unlimited
    else:
        msg_desc = ' - '.join(content)

    await ctx.send(embed=un.confirm_msg(title='Requested pack shorthands:', desc=msg_desc))


# Card search function
@bot.command()
async def c(ctx, *args):
    # Check file to see if it exists
    # and read set ids for further validation
    try:
        with open('pack_info/set_ids.txt') as f:
            content = f.read().splitlines()
    except IOError:
        await ctx.send(embed=un.err_msg(title='Internal error',
                                        desc=f'Error reading packs ids, please contact developer of Neme'))

    # This block validate all options and send error messages
    for i in range(len(args)):
        # split option types and values for each argument
        temp = args[i].split('=')

        # handle text values, split values and merge them back using + for search url
        if temp[0] == 'n' or temp[0] == 'k':
            val = '+'.join(char for char in temp[1].split('+') if char.isalpha())

            # if val is empty then name contains special characters other than +
            if val == '':
                await ctx.send(embed=un.err_msg(title='Invalid text value(s)'))
                return

        # handle digit values for Rarity, Type, Class, Format
        if temp[0] == 'r' or temp[0] == 't' or temp[0] == 'c' or temp[0] == 'f':
            if not uio.validate_range(temp):
                await ctx.send(embed=un.err_msg(title='Invalid digit value(s)'))
                return

        # handle values for Pack
        if temp[0] == 'p':
            found = False
            for line in content:
                if line.split(':')[0] == temp[1]:
                    found = True

            if not found:
                await ctx.send(embed=un.err_msg(title='Invalid pack name(s)'))
                return

    card_id = uc.get_id(args)

    # no card found
    if len(card_id) == 0:
        await ctx.send(embed=un.info_msg(title='No cards found'))
        return

    # more than 10 cards
    if len(card_id) > 10:
        await ctx.send(embed=un.info_msg(title='More than 10 cards found. Please provide more details'))
        return

    # more than 1 card but less than 10
    if 1 < len(card_id) < 11:
        emojis = ['🐗', '🦉', '🐉', '⚰️', '👻', '🎃', '🍌', '🥢', '🍑', '🍺']
        msg = await ctx.send(embed=un.multi_msg(card_id, emojis))

        # add reaction to message based on the length of card_id list
        for i in range(len(card_id)):
            await msg.add_reaction(emojis[i])

        # wait for reaction from user
        ret = await on_reaction(ctx.message.author)

        # retrieve index of emoji correspond to card id
        target = [i for i in range(len(emojis)) if ret['reaction'] == emojis[i]]

        # if the correct user reacted then extract info and send message
        if ret['state'] == 'reacted':
            card_info = uc.extract_info(card_id[target[0]])
            await ctx.send(embed=uc.format_card(card_info, card_id[target[0]]))

        # timed out message
        else:
            await ctx.send(embed=un.info_msg(title=f'{ret["msg"]}'))

        return

    # only one card found
    card_info = uc.extract_info(card_id[0])
    await ctx.send(embed=uc.format_card(card_info, card_id[0]))


@bot.event
async def on_reaction(user_id):
    ret = {'state': 'not reacted', 'reaction': '', 'msg': ''}

    while ret['state'] == 'not reacted':
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10)

            if str(user_id) == str(user):
                ret['state'] = 'reacted'
                ret['reaction'] = str(reaction)
                ret['msg'] = f'{str(user)} reacted with {str(reaction)}'
                print(ret)

        except asyncio.exceptions.TimeoutError:
            ret['state'] = 'timed out'
            ret['msg'] = f'Timed out, please try again'

    return ret


# Deck generator function
@bot.command()
async def d(ctx):
    await ctx.send('Work In Progress')


# Run bot
bot.run(TOKEN)
