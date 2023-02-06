import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import os
from time import sleep
import sys
import PIL
import tkinter.simpledialog
from scripts.main.main import main as script_main

from threading import Thread

if getattr(sys, 'frozen', False):
    #if app is frozen
    os.chdir(os.path.dirname(sys.executable))


class ChoiceDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent, title, choices):
        self.choices = choices
        tkinter.simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        tk.Label(master, text="Que faire avec ?").pack()

        self.var = tk.StringVar()
        self.var.set(self.choices[0])

        option_menu = tk.OptionMenu(master, self.var, *self.choices)
        option_menu.pack()

        return option_menu

    def apply(self):
        self.result = self.var.get()


class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show();



class WindowVariables:
    
    def __init__(self):
        self.is_active = True
        self.is_paused = False
        self.pause_button_text = 'Pause'
        self.kill = False
        
    def change_activity(self):
        self.is_active = not(self.is_active)
        self.is_paused = self.is_paused and self.is_active

    def set_active(self):
        self.is_active = True
        self.set_off_pause()
    
    def set_inactive(self):
        self.is_active = False
        self.set_on_pause()

    def change_pause(self):
        self.is_paused = not(self.is_paused)
        self.pause_button_text = 'Reprendre' if self.is_paused else 'Pause'
    
    def set_on_pause(self):
        self.is_paused = True
        self.pause_button_text = 'Reprendre' 
    
    def set_off_pause(self):
        self.is_paused = False
        self.pause_button_text = 'Pause'
    
    def kill_func(self):
        self.set_on_pause()
        self.set_inactive()
        self.kill = True


def get_add_entry(listbox,entry_var):
    def add_entry():
        """
        Adds an entry to the listbox
        """
        entry = entry_var.get()
        if entry:
            dialog = ChoiceDialog(listbox,"entry", ["kill", "capture", "run"])
            if dialog.result:
                listbox.insert(tk.END, entry.lower()+':'+ dialog.result)
            #listbox.insert(tk.END, entry)
            entry_var.set("")
            listbox.config(height = len(listbox.get(0,tk.END)))
    return add_entry


def get_remove_entry(listbox):
    def remove_entry():
        """
        Removes an entry from the listbox
        """
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])
            listbox.config(height = len(listbox.get(0,tk.END)))
    return remove_entry



def get_update_remove_button(listbox,remove_button):
    def update_remove_button(selection):
        selection = listbox.curselection()
        if not selection:
            remove_button.config(state = tk.DISABLED)
        else:
            remove_button.config(state = tk.NORMAL)
    return update_remove_button





class PathRecorder:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()

    def close_windows(self):
        self.master.destroy()



class Window(tk.Tk):
    def __init__(self, loop):
        self.loop = loop
        self.root = tk.Tk()

        self.window_variables = WindowVariables()

        self.root.title("MeyzhBOT")
        self.root.geometry("580x220")



        s = ttk.Style()
        s.configure('TButton', bg='#FFFF00')


        def run_coroutine(coro):
            asyncio.run_coroutine_threadsafe(coro, self.loop)

        self.run_coroutine = run_coroutine

        self.SCRIPT_PARAMS = {}

        self.FRONT_ITEMS = list()


        ################ SEEK

        self.pk_to_find_listbox = tk.Listbox(self.root)
        self.pk_to_find_entry_var = tk.StringVar()
        self.pk_to_find_entry = tk.Entry(self.root, textvariable=self.pk_to_find_entry_var)
        
        with open('scripts/main/poke_a_capturer.txt','r') as f:
            for line in f:
                self.pk_to_find_listbox.insert(tk.END,line.strip())
                




                
                

        self.pk_to_find_listbox.config(height = len(self.pk_to_find_listbox.get(0,tk.END)))
        self.add_pkmn_to_find_button = tk.Button(self.root, 
                                                text="Ajouter Poke", 
                                                command=get_add_entry(self.pk_to_find_listbox,self.pk_to_find_entry_var))
    
        
        self.remove_pkmn_to_find_button = tk.Button(self.root, 
                                                    text="Supprimer Poke", 
                                                    command=get_remove_entry(self.pk_to_find_listbox))
        self.remove_pkmn_to_find_button.config(state=tk.DISABLED)
        self.pk_to_find_listbox.bind('<<ListboxSelect>>', get_update_remove_button(self.pk_to_find_listbox,self.remove_pkmn_to_find_button))
        
        self.save_pk_to_find_button = tk.Button(self.root, 
                                                text="Sauvegarder", 
                                                command=lambda: self.loop.create_task(self.save_pkmn_to_find()))

        self.SCRIPT_PARAMS['poke_a_capturer'] = list(self.pk_to_find_listbox.get(0,tk.END))


   
        self.LEFT_FRAME  = tk.Frame(self.root)
        self.RIGHT_FRAME = tk.Frame(self.root)


        # WHAT TO DO WITH OTHERS ? 
        self.others_frame = tk.Frame(self.LEFT_FRAME)
        self.others_label = tk.Label(self.others_frame, text="Tous les autres :")
        self.others_label.pack(side="left")
        
        self.SCRIPT_PARAMS['others'] = tk.StringVar(self.others_frame)
        self.SCRIPT_PARAMS['others'].set("run") # default value
        self.all_others_menu = tk.OptionMenu(self.others_frame, self.SCRIPT_PARAMS['others'], *['run', 'kill', 'capture'])

        # MOVEMENT (HORIZONTAL, VERTICAL)
        self.movement_frame = tk.Frame(self.LEFT_FRAME)
        self.movement_label = tk.Label(self.movement_frame, text="Mouvement:")
        self.movement_label.pack(side="left")

        self.SCRIPT_PARAMS['movement'] = tk.StringVar(self.root)
        self.SCRIPT_PARAMS['movement'].set("horizontal")
        self.movement_menu = tk.OptionMenu(self.movement_frame, self.SCRIPT_PARAMS['movement'], "horizontal", "vertical")
        self.movement_menu.pack(side='left')

        
        
        # HEAL EVERY ? COMBAT
        self.option_frame = tk.Frame(self.LEFT_FRAME)
        self.option_label = tk.Label(self.option_frame, text="Soigner tous les:")
        self.option_label.pack(side="left")
        self.option_entry = tk.Entry(self.option_frame, width=3)
        self.option_entry.pack(side="left")     
        self.option_entry.insert(0, "10")
        self.SCRIPT_PARAMS['heal every'] = 10


        self.switch_menu_button = tk.Button(self.RIGHT_FRAME,text="Ouvrir l'enregistreur de chemin", width=25, command=lambda: self.loop.create_task(self.switch_menu()))
        
        # GLOBAL MENU START, STOP, PAUSE ...
        self.button_script = tk.Button(self.RIGHT_FRAME,text="Lancer script", width=10, command=lambda: self.loop.create_task(self.launch_script()))
        self.button_script.pack()        

        self.button_stop_script = tk.Button(self.RIGHT_FRAME,text="Stopper le script", width=10, command=lambda: self.loop.create_task(self.stop_script_func()))        
        self.button_stop_script.pack()
        self.button_stop_script.config(state=tk.DISABLED)

        self.pause_button_text = 'Pause'
        self.button_pause_script = tk.Button(self.RIGHT_FRAME,text=self.pause_button_text, width=10, command=lambda: self.loop.create_task(self.pause_func()))
        self.button_pause_script.pack()
        self.button_pause_script.config(state=tk.DISABLED)

        self.button_quit = tk.Button(self.RIGHT_FRAME,text="Quitter", width=10, command=lambda: self.loop.create_task(self.quit()))
        self.button_quit.pack()

    


        self.LEFT_FRAME.pack(anchor='nw', side="left")
        self.RIGHT_FRAME.pack(anchor='ne', side="right")
        
        self.page_1_buttons = [ self.button_script, 

                                self.option_frame, 
                                self.others_frame,
                                self.movement_frame ,

                                self.button_stop_script, 
                                self.button_pause_script, 
                                self.pk_to_find_listbox,
                                self.pk_to_find_entry,
                                self.add_pkmn_to_find_button,
                                self.remove_pkmn_to_find_button,
                                self.save_pk_to_find_button,
                                
                                self.movement_menu,
                                self.switch_menu_button,
                                self.button_quit,
                                self.all_others_menu]



        ############################ PAGE 2

        self.launch_key_recorder_button = tk.Button(text="Lancer l'enregistreur de touches", width=25, command=lambda: self.loop.create_task(self.launch_key_recorder_func()))


        self.page_2_buttons = [ self.launch_key_recorder_button,
                                self.switch_menu_button,
                                self.button_quit] #TODO: add here the 'chemin' name
        
        self.current_page = 1
        self.key_recorder_is_on = False

    
    async def save_pkmn_to_find(self):
        self.SCRIPT_PARAMS['poke_a_capturer'] = list(self.pk_to_find_listbox.get(0,tk.END))
        print("Poke a capturer sont maintenant : ", self.SCRIPT_PARAMS['poke_a_capturer'])
        with open('scripts/main/poke_a_capturer.txt','w') as f:
            for i in range(self.pk_to_find_listbox.size()):
                f.write(self.pk_to_find_listbox.get(i) + '\n')
                


    async def show(self):
        if self.current_page == 1:   
                for block in self.page_1_buttons:
                    block.pack()
        while not(self.window_variables.kill):
            
            self.root.update()
            await asyncio.sleep(.1)


    async def quit(self):
        self.window_variables.kill_func()
        await asyncio.sleep(2)
        self.root.destroy()

    
    async def launch_script(self):     
        main = script_main

        self.window_variables.set_active()
        self.button_pause_script.config(text=self.window_variables.pause_button_text, state=tk.NORMAL)
        self.button_stop_script.config(state=tk.NORMAL)
        self.button_script.config(text= 'Script actif', state=tk.DISABLED)

        self.SCRIPT_PARAMS['heal every'] = int(self.option_entry.get())


        await main(self)
        

    async def stop_script_func(self):

        self.window_variables.set_inactive()
        self.button_pause_script.config(text=self.window_variables.pause_button_text, state=tk.DISABLED)
        self.button_stop_script.config(state=tk.DISABLED)
        self.button_script.config(text= 'Lancer script', state=tk.NORMAL)

    async def pause_func(self):
        self.window_variables.change_pause()
        self.button_pause_script.config(text=self.window_variables.pause_button_text)


    async def switch_menu(self):
        
        self.current_page = 2 if self.current_page == 1 else 1

        if self.current_page == 2:
            for button in self.page_1_buttons:
                if button != self.switch_menu_button:
                    button.pack_forget()
                else:
                    button.config(text="Retour au menu principal")

            for button in self.page_2_buttons:
                button.pack()
        elif self.current_page == 1:
            for button in self.page_2_buttons:
                if button != self.switch_menu_button:
                    button.pack_forget()
                else:
                    button.config(text="Ouvrir l'enregistreur de chemin")
            for button in self.page_1_buttons:
                button.pack()

    def onKeyPress(self, event):
        #handling arrows
        if event.keysym == 'Up':
            self.keys_recorded.append('up')
        elif event.keysym == 'Down':
            self.keys_recorded.append('down')
        elif event.keysym == 'Left':
            self.keys_recorded.append('left')
        elif event.keysym == 'Right':
            self.keys_recorded.append('right')
        #handling space
        elif event.keysym == 'space':
            self.keys_recorded.append('space')
        else:

            if event.char == '&':
                self.keys_recorded.append('1')
            elif event.char == 'é':
                self.keys_recorded.append('2')
            elif event.char == '"':
                self.keys_recorded.append('3')
            elif event.char == "'":
                self.keys_recorded.append('4')
            elif event.char == '(':
                self.keys_recorded.append('5')
            elif event.char == '-':
                self.keys_recorded.append('6')
            elif event.char == 'è':
                self.keys_recorded.append('7')
            else:
                self.keys_recorded.append(event.char)
        print('You pressed {}\n'.format(event.char, ))
        #await asyncio.sleep(0)

    async def launch_key_recorder_func(self):
        if not(self.key_recorder_is_on):
            self.launch_key_recorder_button.config(text="Stop")
            self.keys_recorded = []
            print('start listening')
            self.key_recorder_is_on = True
            self.root.bind('<KeyPress>', self.onKeyPress)

        else:
            self.launch_key_recorder_button.config(text="Lancer l'enregistreur de touches")
            print('stop listening')
            self.root.unbind('<KeyPress>')
            self.key_recorder_is_on = False
            print(self.keys_recorded)
            with open('scripts/main/aller_soigner.txt', 'w') as f:
                
                
                for idx, key in enumerate(self.keys_recorded):
                    f.write('{}:1\n'.format(key) if idx != len(self.keys_recorded)-1 else '{}:1'.format(key))
                
  
        


        
    
if __name__ == "__main__":
    asyncio.run(App().exec())