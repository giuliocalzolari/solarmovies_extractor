#!/usr/bin/env python

import yaml
import time
import os
import fnmatch
from cli.log import LoggingApp
import gspread
import sys
import json
import traceback
import requests
import urllib
import logging
import datetime
from decimal import Decimal
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import re
import csv
import base64
import urlparse
from urllib import urlretrieve
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer

blocksize = 0
widgets = [ Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
pbar = ProgressBar(widgets=widgets)

def dlProgress(count, blockSize, totalSize):
    if pbar.maxval is None:
        pbar.maxval = totalSize
        pbar.start()

    try:
        pbar.update(min(count*blockSize, totalSize))
    except ValueError:
        pass
    

__author__ = ['Giulio.Calzolari']


class Solarmovie(LoggingApp):


    def main(self):

        self.log.info("Starting")
        ep_list = []
        ep_titles = []
        s = requests.session()
        idx = 0
        r = requests.get(self.params.solarmovie_base+self.params.solarmovie_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.findAll('a', href=True):

            next_ep = False
            idx += 1

            url_ep = self.params.solarmovie_base+tag['href']

            if "episode" not in tag['href']:
                continue

            try:
                url_ep.split("/")[6] 
            except IndexError:
                continue

            if url_ep.split("/")[6] in ep_list:
                continue    
            ep_title = tag.contents[0].strip()

            if "Episode" in ep_title or "links" in ep_title:
                continue
            # print ep_title+"#"
            r1 = requests.get(self.params.solarmovie_base+tag['href'])
            soup1 = BeautifulSoup(r1.text, 'html.parser')
            for ep in soup1.find_all('a', href=True):

                if next_ep:
                    break

                if ep['href'].startswith("/link/show"):

                    if ep.contents[0].strip().startswith("vodlocker"):
                        # print ep['href']
                        # print ep.contents[0].strip()

                        r2 = s.get(self.params.solarmovie_base+ep['href'])
                        soup2 = BeautifulSoup(r2.text, 'html.parser')
                        for final_video in soup2.findAll('a', {'class': 'fullyGreenButton'}, href=True):
                            # print "Final video: "+final_video['href']
                            r3 = s.get(final_video['href'])
                            soup3 = BeautifulSoup(r3.text)
                            r4 = s.get(soup3.find('iframe')["src"])
                            p = re.compile(ur'file:\s"(.*)"')
                            rs = re.search(p, r4.text)
                            if rs:
                                vodlocker_mp4 = rs.group(1)
                                video_title = "%s_%s_%s.mp4" % (url_ep.split("/")[5], url_ep.split("/")[6], ep_title)
                            
                                if video_title in ep_titles:
                                    continue

                                # stupid file url
                                if video_title.endswith("                    (.mp4"):
                                    continue    


                                ep_titles.append(video_title)    
                                if os.path.isfile(video_title):
                                    continue

                                # print video_title
                                # print vodlocker_mp4

                                try:
                                    widgets = [ video_title+': ',Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
                                    pbar = ProgressBar(widgets=widgets)
                                    urlretrieve(vodlocker_mp4,video_title, reporthook=dlProgress)
                                    pbar.finish()
                                except AttributeError:
                                    pass


                                next_ep = True


if __name__ == "__main__":
    app = Solarmovie()
    app.add_param("-c", "--config", help="Change the Configuration file to use",
                 default="./config.yaml", required=False, action="store")
    app.add_param( "--solarmovie_base", help="solarmovie_base",
                 default="https://www.solarmovie.ph", required=False, action="store")   
    app.add_param("-u","--solarmovie_url", help="solarmovie_url ex. /tv/friends-1994/season-5/",
                  required=True, action="store")                     
    app.run()

