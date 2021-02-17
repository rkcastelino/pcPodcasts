import requests
import os
import threading, queue
from bs4 import BeautifulSoup as Soup
import time
import keyboard
from win32gui import GetWindowText, GetForegroundWindow
import csv
import pdb
import json

def setup():
    #Load file
    with open('PodcastURLs.json', 'r') as f:
        url_list = json.loads(f.read())

    #Display titles and list option select
    print('\n')
    print("Podcasts on record: ")
    for idx, podcast in enumerate(url_list):
        print(f'{idx} {podcast["title"]}')
    #print(f"{idx+1}: All feeds")
    print('\n')
    selected_podcast = input('Select podcast to sync: ')

    # Get rss-xml file from Patreon link
    rss_url = url_list[int(selected_podcast)]['url']
    rss_xml = requests.get(rss_url)
    soup = Soup(rss_xml.text, features="xml")

    # Podcast name
    podcast = soup.findAll('title')[0].string

    # Make directory to save episodes to if doesn't already exist
    if not os.path.exists('DownloadedPodcasts/' + podcast):
        os.makedirs('DownloadedPodcasts/' + podcast)

    # Check all episodes currently downloaded
    for root, dirs, files in os.walk("./DownloadedPodcasts/" + podcast):
        for filename in files:
            continue

    # Get each item in feed and iterate through
    item_list = soup.findAll('item')

    return podcast, item_list, files

def monitor():
    while True:
        try:
            monitor_queue.get(False)
            break
        except:
            # Check to make sure terminal in focus and not detecting background keypress
            current_window = (GetWindowText(GetForegroundWindow()))
            try:
                # Just extract last characters which should be primary directory
                current_window = current_window[-10:]
            except:
                pass

            # Quit if right keypress and was in correct window
            if keyboard.is_pressed('q') and current_window == 'pcPodcasts':
                quit_queue.put('quit')
                break

def downloading(podcast, item_list, files):
    for item in item_list:
        try:
            quit_flag = quit_queue.get(False)
            break
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
            with open('DownloadedPodcasts/' + podcast + '/' + title, 'wb') as f:
                f.write(mp3.content)

    title_queue.put('all done')
    monitor_queue.put('quit')

def downloadingAnimation():
    animation = ["      ", " .    ", " . .  ", " . . ."]
    idx = 0
    one_cycle_done = 0

    while True:
        try:
            title = title_queue.get(False)

            if one_cycle_done == 1:
                print('Downloaded "' + old_title + '"        ', flush=True) # Need spaces at end to overwite periods
                idx = 0

            if title=='all done':
                print('All episodes synced!')
                break

            print('Downloading "' + title + '"' + animation[idx % len(animation)], end="\r", flush=True) # Flush is required since using GitBash as terminal
        except queue.Empty:
            old_title = title
            print('Downloading "' + title + '"' + animation[idx % len(animation)], end="\r", flush=True)
            idx += 1
            time.sleep(1)

            one_cycle_done = 1
            pass

def main():
    podcast, item_list, files = setup()

    monitorThread = threading.Thread(target = monitor)
    downloadingThread = threading.Thread(target = downloading, args=(podcast, item_list, files))
    downloadingAnimationThread = threading.Thread(target = downloadingAnimation)

    monitorThread.start()
    downloadingThread.start()
    downloadingAnimationThread.start()

if __name__ == "__main__":
    title_queue = queue.Queue()
    quit_queue = queue.Queue()
    monitor_queue = queue.Queue()
    main()
