import subprocess

from browser import Browser

import threading

b = Browser(port=9222)
subprocess.run(['bin/python', 'walmart.py', 'milk', '9222'])

