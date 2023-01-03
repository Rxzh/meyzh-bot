import tkinter as tk
from tkinter import ttk
import asyncio
import os
from time import sleep

class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show();


class Window(tk.Tk):
    def __init__(self, loop):        

        self.loop = loop
        self.root = tk.Tk()
        self.root.title("MeyzhBOT")
        self.root.geometry("260x260")
        self.script_choice = tk.StringVar(self.root)
        self.script_choice.set("exp") # default value

        scripts = [s.split('/')[-1] for s in os.listdir('scripts') if os.path.isdir(f'scripts/{s}') and s != '__pycache__']

        #scripts = ["Script 1", "Script 2", "Script 3"]
        self.script_menu = tk.OptionMenu(self.root, self.script_choice, *scripts)
        self.script_menu.pack()

        # Create a button to launch the script
        self.launch_button = tk.Button(text="Launch", command=lambda: self.loop.create_task(self.run_script()))
        self.launch_button.pack()

        # Create a button to close the window
        self.quit_button = tk.Button(text="Quit", command=lambda: self.loop.create_task(self.close_window()))
        self.quit_button.pack()

        
        


    async def close_window(self):
        self.root.destroy()
        await asyncio.sleep(.1)

    async def run_script(self):
        # Get the selected script from the dropdown menu
        selected_script = self.script_choice.get()
        # Write code to run the selected script here

        os.system(f"python scripts/{selected_script}/{selected_script}.py")
        await print(f"Running script: {selected_script}")
        
        

    #async def show(self):
    #    self.root.mainloop()
    #    await asyncio.sleep(0)

    async def show(self):
        while True:
            self.root.update()
            await asyncio.sleep(.1)

asyncio.run(App().exec())

