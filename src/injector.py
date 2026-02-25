import subprocess
import time
import os

class TextInjector:
    def __init__(self):
        # Determine if we are on Wayland or X11.
        # Under sudo, WAYLAND_DISPLAY might be stripped. We check XDG_SESSION_TYPE broadly.
        session_type = os.environ.get("XDG_SESSION_TYPE", "")
        wayland_display = os.environ.get("WAYLAND_DISPLAY")
        
        self.wayland = "wayland" in session_type.lower() or wayland_display is not None
        
        if self.wayland:
            print("Detected Wayland display.")
        else:
            print("Detected X11 display.")

    def inject_text(self, text: str):
        if not text:
            return

        if self.wayland:
            # Under Wayland, 'wtype' is preferred for typing directly
            # Fallback: wl-copy then ydotool/wtype for Ctrl+V
            try:
                subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True)
                # Slight delay to ensure clipboard is populated
                time.sleep(0.1)
                # Send Ctrl+V using wtype
                # -M ctrl (press ctrl), -k v (press v key), -m ctrl (release ctrl)
                subprocess.run(['wtype', '-M', 'ctrl', '-k', 'v', '-m', 'ctrl'], check=True)
            except Exception as e:
                print(f"Error executing Wayland paste commands: {e}")
                print("Make sure `wl-clipboard` and `wtype` are installed.")
        else:
            # X11 fallback
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
                time.sleep(0.1)
                subprocess.run(['xdotool', 'key', 'ctrl+v'], check=True)
            except Exception as e:
                print(f"Error executing X11 paste commands: {e}")
                print("Make sure `xclip` and `xdotool` are installed.")

if __name__ == "__main__":
    import sys
    inj = TextInjector()
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello World from Injector!"
    print(f"Injecting: {test_text}")
    print("Wait 3 seconds and focus on a text area...")
    time.sleep(3)
    inj.inject_text(test_text)
    print("Done.")
