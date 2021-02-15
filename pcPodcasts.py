#TO DO:
    # status files
    # test and exceptions?
    # what else need in file other than title? pics?
    # valid title names and other test cases
    # how do podcasts apps determine new content?
    # make directory if doesn't exist
    # function structure
    # trigger download via email reception
    # multithreading and ability to pause or cancel
    # code template- blank python script
    # request to download now or wait till later?
    # if sync interrupted, don't start from scratch
    # generalize away from dndads
    # make folder named based on specific podcast?
    # function commenting
    # line commenting
    # test function which removes episodes to resync, test cases in general?
    # note that uses threding even if already used
    # remove pdb dependency?
    # functions listed on ReadMe.md
    # intro when first run script?
    # cost to constnatly reprint
    # move ToDos to new file
    # set up local git repo
    # add images/gifs to documentation
    # had animation issue with "[No Ads] Ep. 15 - 8 Simple Rules for Dadding my Teenage Paeden" since exceeded line limit, wrote to new line everytime, will probably now need to use curses
    # aknowledging going to quit, more immediate quit, neater command line, only detect input from specific terminal

import requests
import pdb
import os
import threading, queue
from bs4 import BeautifulSoup as Soup
import time
import keyboard

def setup():
    # Get rss-xml file from Pat        reon link
    rss_url = "https://www.patreon.com/rss/dungeonsanddads?auth=71IdjlaUs5U0s9MOuTGm5HMDVFXxNefC"
    rss_xml = requests.get(rss_url)
    soup = Soup(rss_xml.text, features="xml")

    # Make directory to save episodes to if doesn't already exist
    if not os.path.exists('Episodes'):
        os.makedirs('Episodes')

    # Check all episodes currently downloaded
    for root, dirs, files in os.walk("./Episodes"):
        for filename in files:
            continue

    # Get each item in feed and iterate through
    item_list = soup.findAll('item')

    return item_list, files

def monitor():
    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed
                quit_queue.put('quit')
                break  # finishing the loop
        except:
            break  # if user pressed a key other than the given key the loop will break



def downloading(item_list, files):
    quit_flag = 0;

    for item in item_list:
        try:
            quit_flag = quit_queue.get(False)
        except queue.Empty:
            title = item.title.text + '.mp3'
            # Test if title has characters which break file naming
            if title.find('/') | title.find('"'):
                title = title.replace('/', ',')
                title = title.replace('"', "'")

            # Skip file if already downloaded
            if title in files:
                 continue

            # Get specific url, download and save mp3
            mp3_url = item.enclosure.get('url')
            title_queue.put(title[:-4])
            mp3 = requests.get(mp3_url)
            with open('Episodes/' + title, 'wb') as f:
                f.write(mp3.content)
        if quit_flag == 'quit':
            break
    title_queue.put('all done')

def downloadingAnimation():
    animation = ["      ", " .    ", " . .  ", " . . ."]
    idx = 0
    one_cycle_done = 0

    while True:
        try:
            title = title_queue.get(False)

            if one_cycle_done == 1:
                print('Downloaded "' + old_title + '"       ', flush=True)              # Need spaces at end to overwite periods
                idx = 0

            if title=='all done':
                break

            print('Downloading "' + title + '"' + animation[idx % len(animation)], end="\r", flush=True)        # Flush is required since using GitBash as terminal
        except queue.Empty:
            old_title = title
            print('Downloading "' + title + '"' + animation[idx % len(animation)], end="\r", flush=True)        # Flush is required since using GitBash as terminal
            idx += 1
            time.sleep(1)

            one_cycle_done = 1
            pass

def main():
    item_list, files = setup()

    monitorThread = threading.Thread(target = monitor)
    downloadingThread = threading.Thread(target = downloading, args=(item_list, files))
    downloadingAnimationThread = threading.Thread(target = downloadingAnimation)

    monitorThread.start()
    downloadingThread.start()
    downloadingAnimationThread.start()

if __name__ == "__main__":
    title_queue = queue.Queue()
    quit_queue = queue.Queue()
    main()
