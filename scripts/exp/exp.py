
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

def get_attack(bot, script_commande_combat):
    async def attack(TKWindow):
        for row in open(script_commande_combat):
            command,n = row.strip().split(':')
            for _ in range(int(n)):
                pyautogui.press(command)
                #await asyncio.sleep(0.18)
                await asyncio.sleep(0.01)

                while  TKWindow.window_variables.is_paused and \
                        TKWindow.window_variables.is_active:
                    await asyncio.sleep(1)

                if not(TKWindow.window_variables.is_active):
                    return None
                #sleep(0.18)
        #sleep(3)
        await asyncio.sleep(3)
    return attack

def get_heal(bot,script_soin):

    wait_foot = 0.2#0.15 # a pied
    #wait_bike = 0.06 # en velo
   
    async def heal(TKWindow):

        script_soin_L = [row.rstrip() for row in open(script_soin)]
        #wait = wait_bike
        wait = wait_foot


        for row in script_soin_L:

            while await bot.am_i_in_combat():
                pyautogui.press('4')
                await asyncio.sleep(0.2)

            command,n = row.split(':')

            for _ in range(int(n)):

                if command == '&':

                    sleep(2)
                    pyautogui.press('1')
                    sleep(2)
                elif command == 'é':

                    sleep(2)
                    pyautogui.press('2')
                    sleep(2)
                elif command == '"':
                    sleep(2)
                    pyautogui.press('3')
                    sleep(2)
                elif command == "'":
                    sleep(2)
                    pyautogui.press('4')
                    sleep(2)
                elif command == '(':
                    sleep(2)
                    pyautogui.press('5')
                    sleep(2)
                elif command == '-':
                    sleep(0.5)
                    pyautogui.press('6')     
                    sleep(0.5)  

                elif command == 'space':
                    sleep(2)
                    pyautogui.press('space')  
                    sleep(2)   
                else:
                    pyautogui.press(command)
                #sleep(0.2)
                #await asyncio.sleep(0.2)
                #sleep(wait)
                await asyncio.sleep(wait)
                

                while   TKWindow.window_variables.is_paused and \
                        TKWindow.window_variables.is_active:
                    await asyncio.sleep(1)

                if not(TKWindow.window_variables.is_active):
                    print('none returned')
                    return None
            
        await asyncio.sleep(1)

        #sleep(2)
        await asyncio.sleep(2)
    return heal





async def main(TKWindow, heal_every=10):

    #n = input('Aller soigner tous les ? combats (10 par defaut) : ')
    #n = heal_every
    #n = TKWindow.SCRIPS_PARAMS['heal every']
    print('Soins tous les {} combats'.format(TKWindow.SCRIPT_PARAMS['heal every']))


    script_soin = 'scripts/exp/aller_soigner.txt'
    script_commande_combat = 'scripts/exp/commande_combat.txt'
    bot = MeyzhBOT(TKWindow=TKWindow)

    attack = get_attack(bot,script_commande_combat)
    heal   = get_heal(bot,script_soin)
    k = 0

    #sleep(1)
    await asyncio.sleep(1)
    while TKWindow.window_variables.is_active:

        while   not(TKWindow.window_variables.is_paused) and \
                not(await bot.am_i_in_combat())    :
            await bot.moving_routine()

        k+=1
        while   not(TKWindow.window_variables.is_paused) and \
                await bot.am_i_in_combat():
            await attack(TKWindow)
            await asyncio.sleep(3)

        if      not(TKWindow.window_variables.is_paused) and \
                k%TKWindow.SCRIPT_PARAMS['heal every'] == 0:
            
            await heal(TKWindow)
            

        while TKWindow.window_variables.is_paused:
            await asyncio.sleep(1)

    #TKWindow.window_variables.kill_func() # kill the bot

    
if __name__ == "__main__":
    main()