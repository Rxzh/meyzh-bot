from pynput import keyboard
import asyncio


class KeyListener:
    def __init__(self) -> None:     
        self.current_key_sequence = []        

    async def on_press(self, key):
        print('pressed')
        if key == keyboard.Key.left:
            self.current_key_sequence.append('left')
        elif key == keyboard.Key.right:
            self.current_key_sequence.append('right')
        elif key == keyboard.Key.up:
            self.current_key_sequence.append('up')
        elif key == keyboard.Key.down:
            self.current_key_sequence.append('down')
        elif key == keyboard.Key.space:
            self.current_key_sequence.append('space')
        else:
            self.current_key_sequence.append(str(key))
        await asyncio.sleep(0.1)

    async def start_listening(self):

        self.current_key_sequence = []
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener

            self.listener.join()
        
        
    
    def stop_listening(self):
        #self.listener.stop()
        #keyboard.Listener.stop()
        print('stop listening')

    def save_key_list(self):
        print(self.current_key_sequence)
        with open('scripts/exp/aller_soigner.txt', 'w') as file:
            for key in self.current_key_sequence:
                file.write('{}:1\n'.format(key))