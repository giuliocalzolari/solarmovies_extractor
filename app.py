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
from progressbar import ProgressBar, Percentage, Bar

__author__ = ['Giulio.Calzolari']


class Solarmovie(LoggingApp):

    def get_config(self):
        try:
            self.last_load = os.path.getmtime(self.params.config)
            self.config = yaml.load(open(self.params.config))
        except IOError as e:
            self.log.debug(e)
            quit("No Configuration file found at " + self.params.config)

    def main(self):

        self.log.info("Starting")
        self.get_config()
        ep_list = []
        idx = 0
        r = requests.get(self.config["solarmovie_base"]+self.config["solarmovie_url"])
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.findAll('a', href=True):

            next_ep = False
            idx += 1

            url_ep = self.config["solarmovie_base"]+tag['href']

            if "episode" not in tag['href']:
                continue

            if url_ep.split("/")[6] in ep_list:
                continue
            # print url_ep.split("/")
            ep_title = tag.contents[0].strip()

            if "Episode" in ep_title or "links" in ep_title:
                continue
            # print ep_title+"#"
            r1 = requests.get(self.config["solarmovie_base"]+tag['href'])
            soup1 = BeautifulSoup(r1.text, 'html.parser')
            for ep in soup1.find_all('a', href=True):

                if next_ep:
                    break

                if ep['href'].startswith("/link/show"):

                    if ep.contents[0].strip().startswith("vodlocker"):
                        # print ep['href']
                        # print ep.contents[0].strip()

                        r2 = requests.get(self.config["solarmovie_base"]+ep['href'])
                        soup2 = BeautifulSoup(r2.text, 'html.parser')
                        for final_video in soup2.findAll('a', {'class': 'fullyGreenButton'}, href=True):
                            # print "Final video: "+final_video['href']
                            r3 = requests.get(final_video['href'])
                            soup3 = BeautifulSoup(r3.text)
                            r4 = requests.get(soup3.find('iframe')["src"])
                            p = re.compile(ur'file:\s"(.*)"')
                            rs = re.search(p, r4.text)
                            if rs:
                                vodlocker_mp4 = rs.group(1)
                                video_title = "%s_%s_%s.mp4" % (url_ep.split("/")[5], url_ep.split("/")[6], ep_title)
                                # print video_title
                                # print vodlocker_mp4

                                # global variable to be used in dlProgress
                                output = "%s;%s" % (vodlocker_mp4, video_title)
                                print output
                                with open('file.lst', 'a+') as the_file:
                                    the_file.write("%s\n" % (output))
                                next_ep = True


if __name__ == "__main__":
    app = Solarmovie()
    app.add_param("-c", "--config", help="Change the Configuration file to use",
                 default="./config.yaml", required=False, action="store")
    app.run()

