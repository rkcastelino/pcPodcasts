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

import requests
import pdb
import os
import threading
from bs4 import BeautifulSoup as Soup
import time

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

def syncEpisodes(item_list, files):
    for item in item_list:
        title = item.title.text + '.mp3'
        # Test if title has characters which break file naming
        if title.find('/') | title.find('"'):
            title = title.replace('/', ',')
            title = title.replace('"', "'")
        # Skip file if already downloaded
        if title in files:
             continue

        # Start status printing to command line
        stop_animation_flag = False
        downloadingAnimationThread = threading.Thread(target = downloadingAnimation, args=(title[:-4], lambda : stop_animation_flag))
        downloadingAnimationThread.start()

        # Get specific url, download and save mp3
        mp3_url = item.enclosure.get('url')
        stop_animation_flag = True
        downloadingAnimationThread.join()
        with open('Episodes/' + title, 'wb') as f:
            f.write(mp3.content)

def download():
    mp3 = requests.get(mp3_url)

def downloadingAnimation(title, stop_animation_flag):
    animation = ["      ", " .    ", " . .  ", " . . ."]
    idx = 0
    while True:
        print('Downloading "' + title + '"' + animation[idx % len(animation)], end="\r", flush=True)        # Flush is required since using GitBash as terminal
        idx += 1
        if stop_animation_flag():
            print('Downloaded "' + title + '"       ', flush=True)              # Need spaces at end to overwite periods
            break
        time.sleep(1)


def main():
    item_list, files = setup()
    syncEpisodesThread = threading.Thread(target = syncEpisodes, args=(item_list, files))
    syncEpisodesThread.start()

if __name__ == "__main__":
    main()
