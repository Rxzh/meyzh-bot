import tkinter as tk
from tkinter import ttk
import asyncio
import os
from time import sleep
import sys


if getattr(sys, 'frozen', False):
    #if app is frozen
    os.chdir(os.path.dirname(sys.executable))



class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show();


class Window(tk.Tk):
    def __init__(self, loop):
        self.loop = loop
        self.root = tk.Tk()
        self.app_closing = False
        self.stop_script = True

        #couleur jaune
        self.root.config(bg='#FFFF00')

        self.root.title("MeyzhBOT")
        self.root.geometry("260x260")
        self.script_choice = tk.StringVar(self.root)
        self.script_choice.set("exp") # default value
        scripts = [s.split('/')[-1] for s in os.listdir('scripts') if os.path.isdir(f'scripts/{s}') and s != '__pycache__']
        self.script_menu = tk.OptionMenu(self.root, self.script_choice, *scripts)
        self.script_menu.pack()

        #button_block = tk.Button(text="Async func", width=10, command=lambda: self.loop.create_task(self.async_func()))
        #button_block.pack()

        s = ttk.Style()
        s.configure('TButton', bg='#FFFF00')

        button_script = tk.Button(text="Launch script", width=10, command=lambda: self.loop.create_task(self.launch_script()))
        button_script.pack()        

        button_strop_script = tk.Button(text="Stop script", width=10, command=lambda: self.loop.create_task(self.stop_script_func()))        
        button_strop_script.pack()

        button_quit = tk.Button(text="Quit", width=10, command=lambda: self.loop.create_task(self.quit()))
        button_quit.pack()
        

    async def show(self):
        while not(self.app_closing):

            self.root.update()
            await asyncio.sleep(.1)


    async def quit(self):
        self.root.destroy()
        self.app_closing = True
    
    async def async_func(self):
        for _ in range(10):
            print('coucou')
            await asyncio.sleep(1)
    
    async def launch_script(self):
        selected_script = self.script_choice.get()
        

        #TODO import everything before to fit frozen app
        package = "scripts.{}.{}".format(selected_script, selected_script)
        name = "main"
        main = getattr(__import__(package, fromlist=[name]), name)

        self.stop_script = False
        await main(self)

    async def stop_script_func(self):
        self.stop_script = True


    
if __name__ == "__main__":
    asyncio.run(App().exec())