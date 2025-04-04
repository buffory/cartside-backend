import pychrome
import subprocess
import sys
import os

class Browser:
    def __init__(self, port):
        self.chrome = subprocess.Popen([
            f"chrome-linux/chrome",
            f"--remote-debugging-port={port}",
            f"--disk-cache-dir=/dev/null",
            #"--remote-allow-origins=*"
        ], preexec_fn=os.setsid)

        if self.chrome:
            print(f"Browser open: {port}")

    def kill():
        self.chrome.kill()


if __name__ == "__main__":
    b = Browser(port=9222)
