import pychrome
import subprocess
import os
import time
import requests
import base64
import uuid

class Scraper:
    def __init__(self, port):
        #try:
        #    self.browser = pychrome.Browser(url=f"http://localhost:{port}")
        #except ConnectionError:
        print(f"browser not found at {port}, starting a new one")
        subprocess.Popen(["./chrome-linux/chrome", f"--remote-debugging-port={port}", "--disk-cache-dir=/dev/null"], preexec_fn=os.setsid);

        while True:
            try:
                response = requests.get(f"http://localhost:{port}/json/version")
                if response.ok:
                    print(f"browser found on {port}")
                    self.browser = pychrome.Browser(url=f"http://localhost:{port}")
                    break
            except:
                time.sleep(1)

    def scrape(self, url):
        tab = self.browser.new_tab()
        tab.start()

        tab.Page.navigate(url=url)
        tab.wait(5)
        tab.Runtime.enable()
        result = tab.Runtime.evaluate(expression="document.documentElement.outerHTML")
        file_path = f"data/{uuid.uuid4()}.html"
        with open(file_path, 'w') as f:
            f.write(result['result']['value'])
        print(f"saved {url[:20]}... to {file_path}")

        return file_path
