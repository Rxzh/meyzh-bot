

#import pyautogui
import pyautogui

from time import sleep
import PIL
#from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from transformers import ViTForImageClassification, ViTFeatureExtractor
from PIL import Image
import torch
from torch import hub, cuda

#import discord
#from discord.ext import commands
from time import sleep
#import pandas as pd
#from discord_bot import DiscordBot
import asyncio
import os
from threading import Thread
import asyncio

"""
CLASSES : 

- 'NO'
- 'YES'
- combatbox
- evolve
- learnmove
- pokeinfobox
"""


class Sauron:
    def __init__(self, TKWindow):
        self.model = hub.load(  'ultralytics/yolov5',
                                'custom', # yolov5s, yolov5n - yolov5x6 or custom
                                path='sauron_model/best.pt', force_reload=True) #TODO: check if path is ok

        #self.model.conf = 0.4    # confidence threshold (0-1)

        self.TKWindow = TKWindow
        self.inference = self.model(pyautogui.screenshot())
        self.xyxy  = self.inference.pandas().xyxy[0] 
        self.xywh  = self.inference.pandas().xywh[0] 
        self.xywhn = self.inference.pandas().xywhn[0] 

    def inference_func(self, _):
        self.inference = self.model(pyautogui.screenshot())

        # print(self.inference)
        self.xyxy  = self.inference.pandas().xyxy[0] 
        self.xywh  = self.inference.pandas().xywh[0] 
        self.xywhn = self.inference.pandas().xywhn[0] 

    def main(self):
        while self.TKWindow.window_variables.is_active:                
            while self.TKWindow.window_variables.is_paused and self.TKWindow.window_variables.is_active:
                sleep(1)                
            # Continuously perform inference every .5 seconds
            self.inference_func(self.model)
            sleep(2)
            
            #t = Thread(target=self.inference_func, args=(None,))
            #t.start()
            # no need to ascincio.sleep
            
    


class MeyzhBOT:
    
    def __init__(self, TKWindow):

        #ML Models
        self.device = "cuda" if cuda.is_available() else "cpu"
        self.model_pokemon_classifier = ViTForImageClassification.from_pretrained( "imjeffhi/pokemon_classifier").to(self.device)
        self.feature_extractor = ViTFeatureExtractor.from_pretrained('imjeffhi/pokemon_classifier')

        self.TKWindow = TKWindow

        self.sauron = Sauron(TKWindow=self.TKWindow)
    
        t = Thread(target = self.sauron.main)
        t.start()

        self.screen_shape = pyautogui.size()

    
    def global_screenshot(self):
        """
        takes a screenshot and returns a pillow image
        """
        return pyautogui.screenshot()

    def screenshot(self, x1, y1, x2, y2):
        """
        takes a screenshot and returns a pillow image
        """
        return pyautogui.screenshot(region=(x1, y1, x2, y2))
    
    async def process_img(self, img):

        #DEPRECATED
        #results = self.model_sauron_eye(img)

        results = self.sauron.model(img)

        xyxy  = results.pandas().xyxy[0] 
        xywh  = results.pandas().xywh[0] 
        xywhn = results.pandas().xywhn[0] 
        
        return xyxy, xywh, xywhn


    async def am_i_in_combat(self):
        """
        returns True if in combat
        """
        #xyxy, xywh, xywhn = await self.process_img(self.global_screenshot()) # = sauron.xyxy, sauron.xywh, sauron.xywhn
        
        return 'combatbox' in self.sauron.xywhn['name'].values
    
    async def is_there_an_evo(self):
        """
        returns True if there is an evolution
        """
        xyxy, xywh, xywhn = await self.process_img(self.global_screenshot())
        return 'evolve' in xywhn['name'].values
            

    def find_poke_in_img(self, img):
        #if posix
        if os.name == 'posix':
            img = Image.frombytes('RGB', img.size, img.tobytes(), 'raw', 'RGBX') 
            

        extracted = self.feature_extractor(images=img, return_tensors='pt').to(self.device)
        predicted_id = self.model_pokemon_classifier(**extracted).logits.argmax(-1).item()
        predicted_pokemon = self.model_pokemon_classifier.config.id2label[predicted_id]
        return predicted_pokemon

    async def moving_routine(self, times = (.2, .2)): #TODO: rename probas
        
        if self.TKWindow.SCRIPT_PARAMS['movement'].get() == 'vertical':
            for _ in range(3):
                pyautogui.keyDown('up')
                await asyncio.sleep(times[0])
                pyautogui.keyUp('up')
                await asyncio.sleep(0)
                pyautogui.keyDown('down')
                await asyncio.sleep(times[1])
                pyautogui.keyUp('down')
                await asyncio.sleep(0)
        elif self.TKWindow.SCRIPT_PARAMS['movement'].get() == 'horizontal':
            for _ in range(3):
                pyautogui.keyDown('left')
                await asyncio.sleep(times[0])
                pyautogui.keyUp('left')
                await asyncio.sleep(0)
                pyautogui.keyDown('right')
                await asyncio.sleep(times[1])
                pyautogui.keyUp('right')
                await asyncio.sleep(0)

    async def poke_in_combat(self):
        """
        returns the names of the pokemons in combat if in combat (My Poke, Poke Adversaire) else returns (None, None)
        """
        xyxy, xywh, xywhn = await self.process_img(self.global_screenshot())


        #if 'combatbox' in xywhn['name'].values:
        if await self.am_i_in_combat():

            combatbox_xc = xywhn.loc[self.sauron.xywhn['name'] == 'combatbox', 'xcenter'].values[0] * self.screen_shape[0]
            combatbox_yc = xywhn.loc[self.sauron.xywhn['name'] == 'combatbox', 'ycenter'].values[0] * self.screen_shape[1]

            img = self.global_screenshot()

            xmin,ymin,xmax,ymax = xyxy.loc[xyxy['name'] == 'combatbox', ['xmin','ymin','xmax','ymax']].values[0]
            combatbox = img.crop((xmin,ymin,xmax,ymax))
            

            #image quarter
            corner_bottom_left = combatbox.crop((0, combatbox.size[1]/2, combatbox.size[0]/2, combatbox.size[1]))
            corner_bottom_right = combatbox.crop((combatbox.size[0]/2, combatbox.size[1]/2, combatbox.size[0], combatbox.size[1]))
            corner_top_left = combatbox.crop((0, 0, combatbox.size[0]/2, combatbox.size[1]/2))
            corner_top_right = combatbox.crop((combatbox.size[0]/2, 0, combatbox.size[0], combatbox.size[1]/2))

            corner_top_right_bottom_left = corner_top_right.crop((0, corner_top_right.size[1]/2, corner_top_right.size[0], corner_top_right.size[1]))
            corner_top_right_bottom_left_left_half = corner_top_right_bottom_left.crop((0, 0, corner_top_right_bottom_left.size[0]/4, corner_top_right_bottom_left.size[1]))

            my_poke    = corner_bottom_left
            other_poke = corner_top_right_bottom_left_left_half

            return my_poke, other_poke
        else:
            return None, None

    def after_fight(self):
        """
        Routine to do after a fight.
        """
        sleep(1)
        img = self.global_screenshot()

        xyxy, xywh, xywhn = self.sauron.model(img) #self.process_img(img)
        
        #TODO: check if there is an evolution and a move to learn
        pass 
        


        
            

def main():
    bot = MeyzhBOT()

    while 1:
        break # deprecated
        if bot.am_i_in_combat():
            print("====================")
            my_poke, other_poke = bot.poke_in_combat()

            print("{} vs {}".format(bot.find_poke_in_img(my_poke), bot.find_poke_in_img(other_poke)))

if __name__ == "__main__":
    main()
            