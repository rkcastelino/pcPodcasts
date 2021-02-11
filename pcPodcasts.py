#TO DO:
    #Work on filenames
    #log so don't re download every time
    # status files
    # test and exceptions?
    # what else need in file other than title? pics?
    # valid title names and other test cases
    # how do podcasts apps determine new content?
    # make directory if doesn't exist
    # function structure
    # comments
    # trigger download via email reception


import requests
import pdb
import os
from bs4 import BeautifulSoup as Soup

def pcPodcasts():
    rss_url = "https://www.patreon.com/rss/dungeonsanddads?auth=71IdjlaUs5U0s9MOuTGm5HMDVFXxNefC"
    rss_xml = requests.get(rss_url)
    soup = Soup(rss_xml.text, features="xml")

    item_list = soup.findAll('item')

    for root, dirs, files in os.walk("."):
        for filename in files:
            x = 0

    for item in item_list:
        title = item.title.text + '.mp3'
        if title.find('/'):
            title = title.replace('/', ',')
        # if title in files:
        #     break
        mp3_url = item.enclosure.get('url')
        mp3 = requests.get(mp3_url)
        with open('Episodes/' + title, 'wb') as f:
            f.write(mp3.content)

if __name__ == "__main__":
    pcPodcasts()
