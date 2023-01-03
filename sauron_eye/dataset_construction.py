import pyautogui
from time import sleep

def main_loop(dataset_size):
    for i in range(40,60):
        pyautogui.screenshot(f"dataset_message/{i}.png")
        sleep(0.2)


if __name__ == "__main__":
    main_loop(30)
