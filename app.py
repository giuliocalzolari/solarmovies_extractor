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
from collections import OrderedDict
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
        headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 11, "\
        "Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}

        self.log.info("Starting")
        ep_list = OrderedDict()
        ep_titles = []
        s = requests.session()
        idx = 0
        r = requests.get(self.params.solarmovie_base+self.params.solarmovie_url,verify=False, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # print soup.findAll('a', href=True)
         
        for tag in soup.select('.seasonEpisodeList .epname a'):
            if tag['href'] not in ep_list.keys():
                ep_list[tag['href']] = tag.contents[0].strip()
        

        for ep in reversed(ep_list.keys()):
        
            url_ep = self.params.solarmovie_base+ep

            print ep_list[ep]+" : "+url_ep;

            r1 = requests.get(url_ep,verify=False, headers=headers)
            soup1 = BeautifulSoup(r1.text, 'html.parser')
            for ep_link in soup1.select('.movie-table .js-link a'):

                if ep_link['href'].startswith("/link/show"):

                    if ep_link.contents[0].strip().startswith("vodlocker"):
                        # print ep['href']
                        # print self.params.solarmovie_base+ep_link['href']


                        r2 = s.get(self.params.solarmovie_base+ep_link['href'],verify=False, headers=headers)
                        soup2 = BeautifulSoup(r2.text, 'html.parser')
                        for final_video in soup2.findAll('a', {'class': 'fullyGreenButton'}, href=True):
                            # print "Final video: "+final_video['href']
                            r3 = s.get(final_video['href'],verify=False, headers=headers)
                            soup3 = BeautifulSoup(r3.text)
                            if soup3.find('iframe') == None:
                                r4 = s.get(soup3.select('.js-play-iframe-container a')[0]['href'],verify=False, headers=headers)
                            else:
                                r4 = s.get(soup3.find('iframe')["src"],verify=False, headers=headers)

                            p = re.compile(ur'file:\s"(.*)"')
                            rs = re.search(p, r4.text)
                            if rs:
                                vodlocker_mp4 = rs.group(1)
                                video_title = "%s_%s_%s.mp4" % (ep.split("/")[3], ep.split("/")[4], ep_list[ep])
                              
                                if os.path.isfile(video_title):
                                    continue

                                print video_title

                                try:
                                    widgets = [ video_title+': ',Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
                                    pbar = ProgressBar(widgets=widgets)
                                    urlretrieve(vodlocker_mp4,video_title, reporthook=dlProgress)
                                    pbar.finish()
                                except AttributeError:
                                    pass





if __name__ == "__main__":
    app = Solarmovie()
    app.add_param("-c", "--config", help="Change the Configuration file to use",
                 default="./config.yaml", required=False, action="store")
    app.add_param( "--solarmovie_base", help="solarmovie_base",
                 default="https://www.solarmovie.ph", required=False, action="store")   
    app.add_param("-u","--solarmovie_url", help="solarmovie_url ex. /tv/friends-1994/season-5/",
                  required=True, action="store")     
    try:                
        app.run()
    except KeyboardInterrupt:
        print 'Interrupted'
        sys.exit(0)

