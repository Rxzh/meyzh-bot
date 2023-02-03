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


async def back_at_ligue(TKWindow):
    await asyncio.sleep(5)
    pyautogui.press('right')



async def find_first_combat(TKWindow):
    await asyncio.sleep(0.1)
    pyautogui.press('space')
    pyautogui.press('up')



async def main(TKWindow, heal_every=10):

    #n = input('Aller soigner tous les ? combats (10 par defaut) : ')



    bot = MeyzhBOT(TKWindow=TKWindow, movement='horizontal')


    my_pokemons, attacks = [], []
    with open('scripts/exp_ligue/attaques.txt') as f:
        for row in f.readlines():
            my_pokemons.append(row.split(':')[0])
            attacks.append(row.split(':')[1].strip())

    my_pokemons, attacks = my_pokemons[1:], attacks[1:]

    pokemons_ligue = []
    with open('scripts/exp_ligue/config_ligue.txt') as f:
        for row in f.readlines():
            pokemons_ligue.append(row.strip())
    

    #sleep(1)
    last_mine = None

    await asyncio.sleep(1)
    while TKWindow.window_variables.is_active:

        await back_at_ligue(TKWindow)

        while   not(TKWindow.window_variables.is_paused) and \
                not(await bot.am_i_in_combat())    :
            await find_first_combat(TKWindow)

        while await bot.am_i_in_combat():
            await asyncio.sleep(10)
            current_mine, current_ennemy = await bot.poke_in_combat()
            if not(current_mine is None or current_ennemy is None):
                current_mine = bot.find_poke_in_img(current_mine).lower()
                #print('current mine : {}'.format(current_mine))
                current_ennemy = bot.find_poke_in_img(current_ennemy).lower()
                #print('current ennemy : {}'.format(current_ennemy))

                if last_mine is None:
                    last_mine = current_mine

            if current_ennemy == pokemons_ligue[-1]: #last one TODO:replace by -1
                #print('last one, escaping')
                pyautogui.press('4')
                while not ('YES' in bot.sauron.xywhn['name'].values):
                    #print('waiting for YES')
                    #print(bot.sauron.xywhn['name'].values)
                    await asyncio.sleep(2)
                YES_xc = bot.sauron.xywhn.loc[bot.sauron.xywhn['name'] == 'YES', 'xcenter'].values[0] * bot.screen_shape[0]
                YES_yc = bot.sauron.xywhn.loc[bot.sauron.xywhn['name'] == 'YES', 'ycenter'].values[0] * bot.screen_shape[1]

                #print('YES_xc : {}'.format(YES_xc))
                #print('YES_yc : {}'.format(YES_yc))


                pyautogui.moveTo(YES_xc, YES_yc)
                pyautogui.click()
                pyautogui.click()
                await asyncio.sleep(1)
            
            elif current_mine in my_pokemons:
                last_mine = current_mine
                pyautogui.press('1')
                await asyncio.sleep(0.5)
                print('attacking with : {}'.format(attacks[my_pokemons.index(current_mine)]))
                pyautogui.press(attacks[my_pokemons.index(current_mine)])
            else:
                

                await asyncio.sleep(2)
                pyautogui.press(str(my_pokemons.index(last_mine)+2))
    

        while TKWindow.window_variables.is_paused:
            await asyncio.sleep(1)

    #TKWindow.window_variables.kill_func() # kill the bot

    
if __name__ == "__main__":
    main()