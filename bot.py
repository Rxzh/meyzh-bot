import pyautogui
from time import sleep
from IPython.display import clear_output
import PIL
import random
import io
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from transformers import ViTForImageClassification, ViTFeatureExtractor
from PIL import Image
import torch

import discord
from discord.ext import commands
from time import sleep, time

from scripts.discord_bot import DiscordBot


class PokeBot:
    def __init__(self):
        # Loading in Model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = ViTForImageClassification.from_pretrained( "imjeffhi/pokemon_classifier").to(self.device)
        self.feature_extractor = ViTFeatureExtractor.from_pretrained('imjeffhi/pokemon_classifier')


    def screenshot_to_pillow(self, x1, y1, x2, y2):
        """
        takes a screenshot and returns a pillow image
        """
        img = pyautogui.screenshot(region=(x1, y1, x2, y2))
        return PIL.Image.frombytes('RGB', img.size, img.tobytes(), 'raw', 'RGBX')


    def moving_routine(self, probas = (.5, .6),vertical = False):
        if vertical:
            for _ in range(3):
                pyautogui.keyDown('up')
                sleep(probas[0])
                pyautogui.keyUp('up')
                pyautogui.keyDown('down')
                sleep(probas[1])
                pyautogui.keyUp('down')
        else:
            for _ in range(3):
                pyautogui.keyDown('left')
                #sleep(random.random())
                sleep(probas[0])
                pyautogui.keyUp('left')
                
                pyautogui.keyDown('right')
                #sleep(random.random())
                sleep(probas[1])
                pyautogui.keyUp('right')


    def find_oponent_poke(self):
        x1=2150 #OK
        x2=200 #OK
        y1=710 #OK
        y2=200 #OK

        img = self.screenshot_to_pillow(x1, y1, x2, y2)
        
        #plot image
        #img.show()

        extracted = self.feature_extractor(images=img, return_tensors='pt').to(self.device)
        predicted_id =self.model(**extracted).logits.argmax(-1).item()
        predicted_pokemon = self.model.config.id2label[predicted_id]
        
        return predicted_pokemon


    def am_i_in_combat(self, my_poke = 'charizard'):
        x1=1500 #OK
        x2=400 #OK
        y1=1050 #OK
        y2=400 #OK
        
        img = self.screenshot_to_pillow(x1, y1, x2, y2)
        extracted = self.feature_extractor(images=img, return_tensors='pt').to(self.device)
        predicted_id = self.model(**extracted).logits.argmax(-1).item()
        predicted_pokemon = self.model.config.id2label[predicted_id]
        
        #print("predicted poke = ".format(predicted_pokemon))
        if predicted_pokemon.lower()==my_poke:
            #print('EN COMBAT')
            return True
        else:
            return False

    def esquive_poke_sauvage(self, list_of_poke = ['Golbat'], my_poke = 'charizard'):
        in_combat = True
        t0_combat = time()
        while True:
            while not(self.am_i_in_combat(my_poke = my_poke)):
                in_combat = False
                self.moving_routine()
            
            # in combat
            if not(in_combat):
                in_combat = True
                t0_combat = time()
            else:
                if time()-t0_combat>300: # 5 min
                    sleep(2)
                    return 'En combat depuis 5 min, shiny trouvé?'
            
            poke_en_face = self.find_oponent_poke()
            if not(poke_en_face in list_of_poke):
                output_message = '{} trouvé!\n- !control pour controler le bot\n- !restart pour relancer la recherche de Poke'.format(poke_en_face)
                print(output_message)
                return output_message
            else:
                pyautogui.press("4")
                sleep(2)

    
    def recherche_poke_sauvage(self, list_of_poke = ['Dratini', 'Axew'], my_poke = 'charizard'):
        
        in_combat = True
        t0_combat = time()
        while True:
            while not(self.am_i_in_combat(my_poke = my_poke)):
                in_combat = False
                self.moving_routine()
            
            # in combat
            if not(in_combat):
                in_combat = True
                t0_combat = time()
            else:
                if time()-t0_combat>300: # 5 min
                    sleep(2)
                    return 'En combat depuis 5 min, shiny trouvé?'


            poke_en_face = self.find_oponent_poke()

            if poke_en_face in list_of_poke:
                output_message = '{} trouvé!\n- !control pour controler le bot\n- !restart pour relancer la recherche de Poke'.format(poke_en_face)
                print(output_message)
                return output_message
            else:
                pyautogui.press("4")
                sleep(2)
        
    def exp(self, my_poke = 'axew', pokes_not_to_kill = []):
        while True:

            self.click(x=767, y=599)

            while not(self.am_i_in_combat(my_poke = my_poke)):
                self.moving_routine(vertical=True)
            while self.am_i_in_combat(my_poke = my_poke):
                if self.find_oponent_poke() in pokes_not_to_kill:
                    input("Pokemon a capturer, appuyer sur entrer pour continuer")

                pyautogui.press("1")
                sleep(0.2)

            sleep(2)
    
    def click(self, x,y):
        pyautogui.moveTo(x,y)
        sleep(0.1)
        pyautogui.click()
        pyautogui.click()
    


#MODE = 'recherche poke'
MODE = 'exp'
#MODE = 'esquive poke'

if __name__ == "__main__":
    PokeBot = PokeBot()



    while 1:

        if MODE == 'recherche poke':

            poke_trouve_msg = PokeBot.recherche_poke_sauvage(list_of_poke = ['Vulpix','Growlithe'], my_poke='tentacool')

            img = PokeBot.screenshot_to_pillow( x1=2150,
                                                x2=200,
                                                y1=710,
                                                y2=200 )  

        
            arr = io.BytesIO()
            img.save(arr, format='PNG')
            arr.seek(0)
            
            bot = DiscordBot(init_message=poke_trouve_msg, init_picture=arr)    
            bot.run(bot.token)


        elif MODE == 'exp':
            PokeBot.exp(my_poke='meganium', pokes_not_to_kill = ['Dratini', 'Axew', 'Lapras', 'Ralts'])


        elif MODE == 'esquive poke':
            poke_trouve_msg = PokeBot.esquive_poke_sauvage(list_of_poke = ['Riolu','Sandshrew'
                    'Azurill',
                    'Psyduck',
                    'Magikarp',
                    'Staryu',
                    'Spheal',
                    'Tentacool'], my_poke='charizard')

            img = PokeBot.screenshot_to_pillow( x1=2150,
                                                x2=200,
                                                y1=710,
                                                y2=200 )  

        
            arr = io.BytesIO()
            img.save(arr, format='PNG')
            arr.seek(0)
            
            bot = DiscordBot(init_message=poke_trouve_msg, init_picture=arr)    
            bot.run(bot.token)