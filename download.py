#!/usr/bin/env python
from urllib import urlretrieve
import os
from progressbar import ProgressBar, Percentage, Bar

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer

blocksize = 0

def dlProgress(count, blockSize, totalSize):
    if pbar.maxval is None:
        pbar.maxval = totalSize
        pbar.start()

    pbar.update(min(count*blockSize, totalSize))


with open("file.lst", "r") as f:
  for line in f:
    dt = line.strip("\n").split(";")

    if os.path.isfile(dt[1]):
        continue


    widgets = [dt[1]+': ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets)
    urlretrieve(dt[0], dt[1], reporthook=dlProgress)
    pbar.finish()
