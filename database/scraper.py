import PyChromeDevTools
import subprocess
import os
import time
import requests
import base64
import uuid

class Scraper:
    def __init__(self, port):
        self.chrome = PyChromeDevTools.ChromeInterface(host="localhost", port=port)

    def scrape(self, url):
        self.chrome.Page.enable()
        self.chrome.Runtime.enable()
        self.chrome.Page.navigate(url=url)
        self.chrome.wait_event("Page.loadEventFired", timeout=60)

        result, messages = self.chrome.Runtime.evaluate(expression="document.documentElement.outerHTML")
        file_path = f"data/{uuid.uuid4()}.html"
        print(list(result['result']['result'].keys()))
        with open(file_path, 'w') as f:
            f.write(result['result']['result']['value'])
        print(f"saved {url[:20]}... to {file_path}")

        return file_path
