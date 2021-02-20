import requests
import os, json, sys, time
import threading, queue
import keyboard
from bs4 import BeautifulSoup as Soup
from win32gui import GetWindowText, GetForegroundWindow
import pdb
from multiprocessing import Process, Pipe
# remove pipe if don't need
# remove threading/queue if don't need

def get_title(url):
    # Get rss-xml file from Patreon link
    rss_xml = requests.get(url)
    soup = Soup(rss_xml.text, features="xml")

    # Podcast name
    title = soup.findAll('title')[0].string

    return title, soup


def print_feeds(url_list):
    #Display titles and list option select
    print('\n')
    print("Podcasts on record: ")
    for idx, podcast in enumerate(url_list):
        print(f'{idx} {podcast["title"]}')
    #print(f"{idx+1}: All feeds")
    print('\n')
    selected_podcast = int(input('Select podcast to sync: '))

    return selected_podcast

def setup():
    #Load file
    with open('PodcastURLs.json', 'r') as f:
        data = f.read()
        try:
            url_list = json.loads(data)
        except:
            print('No RSS feeds on record, please add one to continue!')
            sys.exit()

    selected_podcast = print_feeds(url_list)
    title, soup = get_title(url_list[selected_podcast]['url'])

    # Make directory to save episodes to if doesn't already exist
    if not os.path.exists('DownloadedPodcasts/' + title):
        os.makedirs('DownloadedPodcasts/' + title)

    # Check all episodes currently downloaded
    for root, dirs, files in os.walk("./DownloadedPodcasts/" + title):
        for filename in files:
            continue

    # Get each item in feed and iterate through
    item_list = soup.findAll('item')

    return title, item_list, files


def monitor():
    while True:
        # Check to make sure terminal in focus and not detecting background keypress
        current_window = (GetWindowText(GetForegroundWindow()))
        try:
            # Just extract last characters which should be primary directory
            current_window = current_window[-10:]
        except:
            pass

        # Quit if right keypress and was in correct window
        if keyboard.is_pressed('q') and current_window == 'pcPodcasts':
            sys.exit()
            break

def downloading(podcast_title, item_list, files):
    for item in item_list:
        title = item.title.text + '.mp3'    # Title from here on out refers to episode title
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
        with open('DownloadedPodcasts/' + podcast_title + '/' + title, 'wb') as f:
            f.write(mp3.content)

    title_queue.put('all done')


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


def crud():
    operation_choice = int(input("""Select operation:
    0 Add feed
    1 Remove feed

    > """))

    if operation_choice == 0:
        with open('PodcastURLs.json', 'r') as f:
            data = f.read()
            url_list = json.loads(data)

        url = input("Paste RSS url: ")
        title, soup = get_title(url)
        url_list.append({'title':title, 'url':url})

        with open('PodcastURLs.json', 'w') as f:
            json.dump(url_list,f)

    elif operation_choice == 1:
        with open('PodcastURLs.json', 'r') as f:
            data = f.read()
            url_list = json.loads(data)

        selected_podcast = print_feeds(url_list)
        del url_list[selected_podcast]
        with open('PodcastURLs.json', 'w') as f:
            json.dump(url_list,f)


def sync():
    title, item_list, files = setup()

    downloadingThread = threading.Thread(target = downloading, args=(title, item_list, files))
    downloadingAnimationThread = threading.Thread(target = downloadingAnimation)
    monitorThread = threading.Thread(target = monitor)

    downloadingThread.start()
    downloadingAnimationThread.start()
    monitorThread.start()

def main():
    while True:
        operation_choice = input("""Select operation:
        0 Add/remove podcast feed
        1 Synchronize podcast

        > """)

        if int(operation_choice) == 0:
            crud()
        elif int(operation_choice) == 1:
            sync()
        input("Press enter to continue or q to exit.")


if __name__ == "__main__":
    title_queue = queue.Queue()
    main()
