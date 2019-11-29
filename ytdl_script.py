# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 17:09:14 2019

@author: Saurabh
"""

from __future__ import unicode_literals
import youtube_dl
import time
import sys
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
        pass
        
class downloadlogger(object):
    def debug(self, msg):
        if 'ffmpeg' in msg:
            if 'Embedding' in msg:
                print(msg+'\n')
            else:
                print(msg)
        elif 'already been downloaded' in msg:
            print(msg)

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

def my_hook(progress):
    global pbar, new, lastknownsize
    if progress['status'] == 'downloading':
        if new == True:
            print('Downloading:', progress['filename'])
            pbar = tqdm(total = progress['total_bytes'], unit='B', unit_scale=True, unit_divisor=1024, leave=False, desc='[download]', dynamic_ncols=True, file=sys.stdout)
            pbar.update(progress['downloaded_bytes'])
            new = False
            lastknownsize = progress['downloaded_bytes']
        else:
            pbar.update(progress['downloaded_bytes'] - lastknownsize)
            lastknownsize  = progress['downloaded_bytes']
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


def download_video(video_url, video_name):
    global start
    opts_download = {
        'format': '160',
        'merge_output_format': 'mkv',
        'logger': downloadlogger(),
        'progress_hooks': [my_hook],
        'writesubtitles': True,
        'subtitlesformat': 'srt',
        'subtitleslang': ['en'],
        'outtmpl': video_name+'.%(ext)s',
        'postprocessors': [
            {
                'key' : 'FFmpegSubtitlesConvertor',
                'format' : 'srt'
            },
            {
                'key' : 'FFmpegEmbedSubtitle',
            }
        ]
    }
    start = time.time()
    with youtube_dl.YoutubeDL(opts_download) as ydl:
        ydl.download([video_url])
        
"""downloadvideo('https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-004-computation-structures-spring-2017/c1/c1s2/','test')"""