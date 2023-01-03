
import os
import pyautogui
import sys
sys.path.append('scripts')
from newbot import MeyzhBOT
from time import sleep
import asyncio
from discord_bot import DiscordBot

def get_attack(bot,script_commande_combat):
    async def attack(TKWindow):
        for row in open(script_commande_combat):
            command,n = row.strip().split(':')
            for _ in range(int(n)):
                pyautogui.press(command)
                await asyncio.sleep(0.18)
                if TKWindow.stop_script == True:
                    break
                #sleep(0.18)
        #sleep(3)
        await asyncio.sleep(3)
    return attack

def get_heal(bot,script_soin):

    wait_foot = 0.2#0.15 # a pied
    wait_bike = 0.06 # en velo
   
    async def heal(TKWindow):

        script_soin_L = [row.rstrip() for row in open(script_soin)]
        wait = wait_bike


        for row in script_soin_L:

            while await bot.am_i_in_combat():
                pyautogui.press('4')
                await asyncio.sleep(0.2)

            if 'HEAL' in row:
                heal_index = script_soin_L.index(row)
                wait = wait_foot
                continue

            command,n = row.split(':')
            for _ in range(int(n)):
                pyautogui.press(command)
                #sleep(0.2)
                await asyncio.sleep(0.2)
                #sleep(wait)
                await asyncio.sleep(wait)
                
                if TKWindow.stop_script == True:
                    break
        #sleep(1)
        await asyncio.sleep(1)
        pyautogui.press('2')
        #sleep(1)
        await asyncio.sleep(1)

        wait = wait_bike
        for row in list(reversed(script_soin_L[:heal_index])):
            command,n = row.split(':')
            if command == 'up':
                command = 'down'
            elif command == 'down':
                command = 'up'
            elif command == 'left':
                command = 'right'
            elif command == 'right':
                command = 'left'

            for _ in range(int(n)):
                pyautogui.press(command)
                #sleep(wait)
                await asyncio.sleep(wait)
        #sleep(2)
        await asyncio.sleep(2)
    return heal


async def main(TKWindow):

    n = input('Aller soigner tous les ? combats (10 par defaut) : ')

    script_soin = 'scripts/exp/aller_soigner.txt'
    script_commande_combat = 'scripts/exp/commande_combat.txt'
    bot = MeyzhBOT()

    attack = get_attack(bot,script_commande_combat)
    heal   = get_heal(bot,script_soin)
    k = 0

    #sleep(1)
    await asyncio.sleep(1)
    while TKWindow.stop_script == False:

        while not(await bot.am_i_in_combat()) and TKWindow.stop_script == False:
            await bot.moving_routine(vertical=True)

        k+=1
        while await bot.am_i_in_combat() and TKWindow.stop_script == False:
            await attack(TKWindow)
            #sleep(3)
            await asyncio.sleep(3)
        if k==int(n) and TKWindow.stop_script == False:
            await heal(TKWindow)
            k=0


    
if __name__ == "__main__":
    main()