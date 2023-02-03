import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import os
from time import sleep
import sys
import PIL

from scripts.exp.exp import main as exp_main
from scripts.exp_ligue.exp_ligue import main as exp_ligue_main
from scripts.seek.seek import main as seek_main

from threading import Thread

if getattr(sys, 'frozen', False):
    #if app is frozen
    os.chdir(os.path.dirname(sys.executable))



class Scripts:
    def __init__(self) -> None:
        self.all = {'exp': exp_main,
                    'exp_ligue': exp_ligue_main,
                    'seek': seek_main}


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
            listbox.insert(tk.END, entry)
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
        self.root.geometry("260x360")
        self.script_choice = tk.StringVar(self.root)
        self.script_choice.set("exp") # default value

        if getattr(sys, 'frozen', False):        
            MAIN_PATH = os.path.abspath(os.path.join(os.path.abspath(sys.executable), os.pardir)) 
            scripts = [s.split('/')[-1] for s in os.listdir(os.path.join(MAIN_PATH,'scripts')) if os.path.isdir(os.path.join(MAIN_PATH,f'scripts/{s}')) and s != '__pycache__']
        else:   
            scripts = [s.split('/')[-1] for s in os.listdir('scripts') if os.path.isdir(f'scripts/{s}') and s != '__pycache__']
        self.script_menu = tk.OptionMenu(self.root, self.script_choice, *scripts)
        self.script_menu.pack()

        s = ttk.Style()
        s.configure('TButton', bg='#FFFF00')


        def run_coroutine(coro):
            asyncio.run_coroutine_threadsafe(coro, self.loop)

        self.run_coroutine = run_coroutine

        self.SCRIPT_PARAMS = {}

        self.PAGES = {}


        ################ SEEK

        self.pk_to_find_listbox = tk.Listbox(self.root)
        self.pk_to_find_entry_var = tk.StringVar()
        self.pk_to_find_entry = tk.Entry(self.root, textvariable=self.pk_to_find_entry_var)
        
        with open('scripts/seek/poke_a_capturer.txt','r') as f:
            for line in f:
                self.pk_to_find_listbox.insert(tk.END, line.strip())

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


        self.PAGES['seek'] = [  self.pk_to_find_listbox,
                                self.pk_to_find_entry,
                                self.add_pkmn_to_find_button,
                                self.remove_pkmn_to_find_button,
                                self.save_pk_to_find_button]



        ################ EXP
        ## SOIN

        self.option_frame = tk.Frame(self.root)
        self.option_frame.pack(anchor="n")
        self.option_label = tk.Label(self.option_frame, text="Soigner tous les ? combats:")
        self.option_label.pack(side="left")
        self.option_entry = tk.Entry(self.option_frame, width=3)
        self.option_entry.pack(side="left")     
        self.option_entry.insert(0, "10")
        self.SCRIPT_PARAMS['heal every'] = 10
        self.switch_menu_button = tk.Button(text="Ouvrir l'enregistreur de chemin", width=25, command=lambda: self.loop.create_task(self.switch_menu()))
        
        #################### OVERALL


        self.button_script = tk.Button(text="Lancer script", width=10, command=lambda: self.loop.create_task(self.launch_script()))
        self.button_script.pack()        

        self.button_stop_script = tk.Button(text="Stopper le script", width=10, command=lambda: self.loop.create_task(self.stop_script_func()))        
        self.button_stop_script.pack()
        self.button_stop_script.config(state=tk.DISABLED)

        self.pause_button_text = 'Pause'
        self.button_pause_script = tk.Button(text=self.pause_button_text, width=10, command=lambda: self.loop.create_task(self.pause_func()))
        self.button_pause_script.pack()
        self.button_pause_script.config(state=tk.DISABLED)


        self.button_quit = tk.Button(text="Quitter", width=10, command=lambda: self.loop.create_task(self.quit()))
        self.button_quit.pack()

        self.page_1_buttons = [ self.button_script, 
                                self.option_frame,
                                self.button_stop_script, 
                                self.button_pause_script, 
                                self.switch_menu_button,
                                self.button_quit]

        self.PAGES['exp'] = [self.switch_menu_button, self.option_frame]



        self.SCRIPT_PARAMS['movement'] = tk.StringVar(self.root)
        #self.movement_choice = tk.StringVar(self.root)
        self.SCRIPT_PARAMS['movement'].set("horizontal")
        #self.movement_choice.set("horizontal") # default value        
        

        self.movement_menu = tk.OptionMenu(self.root, self.SCRIPT_PARAMS['movement'], "horizontal", "vertical")
        self.movement_menu.pack()


        ############################ PAGE 2

        self.launch_key_recorder_button = tk.Button(text="Lancer l'enregistreur de touches", width=25, command=lambda: self.loop.create_task(self.launch_key_recorder_func()))


        self.page_2_buttons = [ self.switch_menu_button,
                                self.launch_key_recorder_button,
                                self.button_quit]
        
        self.current_page = 1
        self.key_recorder_is_on = False

    
    async def save_pkmn_to_find(self):
        self.SCRIPT_PARAMS['poke_a_capturer'] = list(self.pk_to_find_listbox.get(0,tk.END))
        print("Poke a capturer sont maintenant : ", self.SCRIPT_PARAMS['poke_a_capturer'])
        with open('scripts/seek/poke_a_capturer.txt','w') as f:
            for i in range(self.pk_to_find_listbox.size()):
                f.write(self.pk_to_find_listbox.get(i) + '\n')
                


    async def show(self):
        while not(self.window_variables.kill):
            
            if self.current_page == 1:   
                for page in self.PAGES.keys():
                    if page != self.script_choice.get():
                        for button in self.PAGES[page]:
                            button.pack_forget()  
                    else:
                        for button in self.PAGES[page]:
                            button.pack()           
            
                if self.script_choice.get() == 'exp' and False:                             
                    self.option_frame.pack(after=self.script_menu, before=self.button_script)
                    self.switch_menu_button.pack()

                elif self.script_choice.get() == 'seek' and False:

                    #for page in self.PAGES.keys():
                    #self.option_frame.pack_forget()
                    #self.switch_menu_button.pack_forget()

                    self.pk_to_find_listbox.pack()
                    #self.pk_to_find_entry_var.pack()
                    self.pk_to_find_entry.pack()
                    self.add_pkmn_to_find_button.pack()
                    self.remove_pkmn_to_find_button.pack()

                    #self.poke_to_find.pack()

                else:

                    pass
                    #self.option_frame.pack_forget()
                    #self.switch_menu_button.pack_forget()

            self.root.update()
            await asyncio.sleep(.1)


    async def quit(self):
        self.window_variables.kill_func()
        await asyncio.sleep(2)
        self.root.destroy()

    
    async def async_func(self):
        for _ in range(10):
            print('coucou')
            await asyncio.sleep(1)
    
    async def launch_script(self):
        selected_script = self.script_choice.get()        
        main = Scripts().all[selected_script]

        self.window_variables.set_active()
        self.button_pause_script.config(text=self.window_variables.pause_button_text, state=tk.NORMAL)
        self.button_stop_script.config(state=tk.NORMAL)
        self.button_script.config(text= 'Script actif', state=tk.DISABLED)

        self.SCRIPT_PARAMS['heal every'] = int(self.option_entry.get())

        if selected_script == 'exp':
            await main(self, heal_every = int(self.option_entry.get())) #TODO to deprecate
        else:
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
            with open('scripts/exp/aller_soigner.txt', 'w') as f:
                
                
                for idx, key in enumerate(self.keys_recorded):
                    f.write('{}:1\n'.format(key) if idx != len(self.keys_recorded)-1 else '{}:1'.format(key))
                
  
        


        
    
if __name__ == "__main__":
    asyncio.run(App().exec())