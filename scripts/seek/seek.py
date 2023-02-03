#import os
import pyautogui
import sys
sys.path.append('scripts')

import tkinter as tk

#if frozen:
if getattr(sys, 'frozen', False):
    from scripts.newbot import MeyzhBOT
else:
    from newbot import MeyzhBOT
    
from time import sleep
import asyncio
#from discord_bot import DiscordBot


async def run_away(TKwindow):
    await asyncio.sleep(1)
    pyautogui.press('4')

async def capture(TKwindow):
    await asyncio.sleep(4)
    pyautogui.press('3')
    await asyncio.sleep(1)
    pyautogui.press('1')


async def main(TKWindow):

    AUTO_CAPURE = True


    """
    poke_to_find = list()
    for row in open('scripts/seek/poke_a_capturer.txt'):
        poke_to_find.append(row.rstrip())
    """
    
    bot = MeyzhBOT(TKWindow=TKWindow)

    await asyncio.sleep(1)
    while TKWindow.window_variables.is_active:

        while   not(TKWindow.window_variables.is_paused) and \
                not(await bot.am_i_in_combat())    :
            await bot.moving_routine()

        while   not(TKWindow.window_variables.is_paused) and \
                await bot.am_i_in_combat():

            await asyncio.sleep(2)
            my_poke, other_poke = await bot.poke_in_combat()

            if other_poke is not None:
                other_poke = bot.find_poke_in_img(other_poke)

                if not(other_poke.lower() in TKWindow.SCRIPT_PARAMS['poke_a_capturer']):
                    await run_away(TKWindow)
                    await asyncio.sleep(5)
                else:
                    if AUTO_CAPURE:
                        print('{} is in the list, capture auto'.format(other_poke))
                        await capture(TKWindow)
                        await asyncio.sleep(6)
                    else:
                        print('{} is in the list, pause pour capturer'.format(other_poke))
                        TKWindow.window_variables.set_on_pause()
                        await asyncio.sleep(6)
            

        while TKWindow.window_variables.is_paused:
            await asyncio.sleep(1)