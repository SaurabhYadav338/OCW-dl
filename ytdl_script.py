# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 17:09:14 2019

@author: Saurabh
"""

from __future__ import unicode_literals
import youtube_dl
import time
from tqdm import tqdm

availableformats = ''
format_codes = []
start = 0
new = True
pbar = None
lastknownsize = 0
class formatlogger(object):
    def debug(self, msg):
        global availableformats
        if 'available formats for' in msg.lower():
            availableformats = msg

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        
class downloadlogger(object):
    def debug(self, msg):
        if 'ffmpeg' in msg:
            print(msg)
        elif 'already been downloaded' in msg:
            print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(progress):
    global pbar, new, lastknownsize
    print(progress)
    if progress['status'] == 'downloading':
        if new == True:
            print('Downloading:', progress['filename'])
            pbar = tqdm(total = progress['total_bytes'], unit='B', unit_scale=True, unit_divisor=1024, leave=False, desc='[download]', dynamic_ncols=True)
            pbar.update(progress['downloaded_bytes'])
            new = False
            lastknownsize = progress['downloaded_bytes']
        else:
            pbar.update(progress['downloaded_bytes'] - lastknownsize)
            lastknownsize  = progress['downloaded_bytes']
#        status = f"\r{round(progress['downloaded_bytes']/1048576, 2)}/{progress['_total_bytes_str']} {progress['_percent_str']} at {progress['_speed_str']} ETA {progress['_eta_str']}"
#        status += ' '*(70 -len(status))
#        print(status, end="")
    elif progress['status'] == 'finished':
        if new != True:
            pbar.close()
        new = True
        global start
        elapsed = time.time() - start
        elapsed = round(elapsed)
        elapsed_minutes = int(elapsed/60)
        elapsed_seconds = elapsed%60
        if(elapsed_minutes != 0):
            elapsed_time = str(elapsed_minutes)+' minutes '+str(elapsed_seconds)+' seconds'
        else:
            elapsed_time = str(elapsed_seconds)+' seconds'
        status = f"\rDownloaded {progress['_total_bytes_str']} in {elapsed_time}"
        status += ' '*(70 - len(status))
        print(status)
        start = time.time()
        
        
        
opts_format = {
    'logger': formatlogger(),
    'listformats': 'true',
}


def grabformats(videopage):
    with youtube_dl.YoutubeDL(opts_format) as ydl:
        ydl.download([videopage])
    global format_codes
    format_codes = [int(entry[0:3].strip()) for entry in (availableformats.splitlines())[2:]]
    print(format_codes)


def downloadvideo(videopage):
    global start
    opts_download = {
        'format': 'bestvideo',
        'merge_output_format': 'mkv',
        'logger': downloadlogger(),
        'progress_hooks': [my_hook],
    }
    start = time.time()
    with youtube_dl.YoutubeDL(opts_download) as ydl:
        ydl.download([videopage])
        
"""downloadvideo('https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-004-computation-structures-spring-2017/c1/c1s2/')"""