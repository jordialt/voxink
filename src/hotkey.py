import time
import keyboard
from src import config

class HotkeyListener:
    def __init__(self, key_name=config.RECORD_HOTKEY, on_press=None, on_release=None):
        # Allow passing things like 'alt gr' instead of 'Key.alt_gr'
        self.key_name = key_name.replace("Key.", "").replace("_", " ")
        self.on_press = on_press
        self.on_release = on_release
        self.is_listening = False
        
        # Prevent repeat triggers if key is held
        self._is_pressed = False

    def _on_event(self, event):
        if not self.is_listening:
            return
            
        # We check both strict name ('alt gr') and aliases just in case
        if event.name == self.key_name or (self.key_name == "alt gr" and event.name == "right alt"):
            if event.event_type == keyboard.KEY_DOWN:
                if not self._is_pressed:
                    self._is_pressed = True
                    if self.on_press:
                        self.on_press()
            elif event.event_type == keyboard.KEY_UP:
                if self._is_pressed:
                    self._is_pressed = False
                    if self.on_release:
                        self.on_release()

    def start(self):
        self.is_listening = True
        keyboard.hook(self._on_event)
        print(f"Listening for '{self.key_name}' globally (using evdev/keyboard module).")

    def stop(self):
        self.is_listening = False
        keyboard.unhook(self._on_event)

if __name__ == "__main__":
    def on_press():
        print("Hotkey Pressed!")
    def on_release():
        print("Hotkey Released!")

    listener = HotkeyListener(on_press=on_press, on_release=on_release)
    listener.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
