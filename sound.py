import pygame


def ring():
    """
    play a dring sound
    """

    # import the required module
    import os

    if os.name == 'nt':
        # for windows
        import winsound


        # frequency is set to 2500 hertz
        frequency = 2500

        # duration is set to 1000 ms == 1 second
        duration = 1000

        # play the ring sound
        winsound.Beep(frequency, duration)
    elif os.name == 'posix':
        # for linux
        import subprocess

        # play the ring sound
        subprocess.call(['play', '-n', 'synth', '1', 'sin', '800'])
    






