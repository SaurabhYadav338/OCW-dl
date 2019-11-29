# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:49:16 2019

@author: Saurabh
"""

from bs4 import BeautifulSoup
import urllib3
import certifi
import time
import re
import os
from ytdl_script import download_video
from resource_grabber import download_file
from util import sanitize_fs_element


http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
total_videos = 0
total_files = 0
useful_file_formats = {'pdf', 'zip'}

def gethtml(resource_url):
    start = time.time()
    print("Requesting:", resource_url)
    time.clock() 
    httpresponse = http.request("GET", resource_url)
    print("Time Taken:", time.time() - start, "seconds")
    print("Successful")
    return [httpresponse.status, httpresponse.data]

def generate_structure(course_page):
    parsetree = BeautifulSoup(course_page, 'lxml')
    navs = parsetree.find_all(id="course_nav")
    structure = []
    for nav in navs:
        navitem = nav.find('li')
        while navitem is not None:
            a_menu = False
            for item in navitem.find_all('a'):
                if item['href'] is '#':
                    a_menu = True
                    menu = (item.find_parent('div')).find_parent('div')
                    menu_title = (item.find_next_sibling('a').string).strip()
                    subsections = (menu.find('ul')).find_all('a')
                    menu_content = []
                    for section in subsections:
                        linktext = section.string
                        if linktext is not None:
                            if '.' not in section['href'].split('/')[-1]:
                                print(section['href'].split('/')[-1])
                                section['href'] = section['href']+'/'
                            menu_content.append({'type' : 'section',
                                                 'title' : linktext.strip(),
                                                 'url' : 'https://ocw.mit.edu'+section['href'],
                                                 'files' : [],
                                                 'videos': []})
                    structure.append({'type' : 'menu',
                                      'title' : menu_title,
                                      'content' : menu_content})
                else:
                    linktext = item.string
                    if linktext is not None:
                        if '.' not in item['href'].split('/')[-1]:
                            print(item['href'].split('/')[-1])
                            item['href'] = item['href'] + '/'
                        structure.append({'type' : 'section',
                                          'title' : linktext.strip(),
                                          'url' : 'https://ocw.mit.edu'+item['href'],
                                          'files' : [],
                                          'videos' : []})
                if a_menu:
                    break
            navitem = navitem.find_next_sibling('li')
    return structure


def parse_section(section):
    httpresponse = gethtml(section['url'])
    if (httpresponse[0] != 200):
        exit("Unable to fetch Video listing")
    videolist = []
    global total_videos
    global total_files
    parsetree = BeautifulSoup(httpresponse[1], 'lxml')
    course_main = parsetree.find('main')
    downloadable_content = []
    for link in course_main.find_all('a'):
        file_format = link['href'].split('.')[-1].strip()
        if link.string is not None:
            if file_format in useful_file_formats and 'transcript' not in link.string.strip() and 'Transcript' not in link.string.strip():
                host = link['href'].split('/')[0]
                if len(host.strip()) is 0:
                    downloadable_content.append("https://ocw.mit.edu" + link['href'])
                else:
                    downloadable_content.append(link['href'])
    total_files += len(downloadable_content)
    section['files'] = downloadable_content
    if course_main['id'] == 'course_inner_media_gallery':
        for media in course_main.find_all(class_= 'medialisting'):
            videolink = media.find('a')
            videolist.append([videolink['title'], "https://ocw.mit.edu" + videolink['href']+'/'])
    elif course_main.find(class_= 'navigation pagination'):
        paging_bar = course_main.find(class_= 'navigation pagination')
        for media in paging_bar.find_all(id = re.compile('flp_btn_.*')):
            videolink = media.find('a')
            nav_page = gethtml("https://ocw.mit.edu" + videolink['href']+'/')
            page_parsetree = BeautifulSoup(nav_page[1], 'lxml')
            if page_parsetree.find(id = 'media_embed') or page_parsetree.find(class_= 'inline-video'):
                videotitle = media.find('span')
                videolist.append([videotitle.string.strip(), "https://ocw.mit.edu" + videolink['href']+'/'])
    elif course_main.find(id = 'media-embed') or course_main.find(class_= 'inline-video'):
        popup_video = False
        if course_main.find(class_= 'inline-video'):
            inline_video = course_main.find(class_= 'inline-video')
        else:
            inline_video = course_main.find(id = 'media-embed')
        for parent in inline_video.parents:
            if parent.find(class_= 'popup_block'):
                popup_video = True
                break
        if popup_video:
            popup = course_main.find(class_='poplight pagecontainer')
            yt_embedlink = popup['onclick'].split(',')[3]
            video_link = 'https://www.youtube.com/watch?v='+yt_embedlink.split('/')[-1]
        else:
            video_link = section['url']
        videotitle = parsetree.find('meta', {'name' : 'WT.cg_s'})
        videolist.append([videotitle['content'].strip(), video_link])
    section['videos'] = videolist
    if len(videolist) is not 0:
        total_videos = total_videos + len(videolist)
        print("Videos found:\n")
        print(*videolist, sep="\n")



def extract_resources(course_structure):
    for item in course_structure:
        if item['type'] == 'section':
            parse_section(item)
        elif item['type'] == 'menu':
            for menuitem in item['content']:
                parse_section(menuitem)


def download_resources(course_structure, course_name):
    course_name = sanitize_fs_element(course_name)
    try:
        os.mkdir(course_name)
    except FileExistsError:
        # directory already exists
        pass
    os.chdir(course_name)
    base_dir = os.getcwd()
    for item in course_structure:
        if item['type'] == 'section':
            section_created = False
            if len(item['files']) is not 0:
                if not section_created:
                    dir = sanitize_fs_element(item['title'])
                    os.makedirs(dir, exist_ok=True)
                    os.chdir(dir)
                    section_created = True
                for file in item['files']:
                    download_file(file)
            if len(item['videos']) is not 0:
                if not section_created:
                    dir = sanitize_fs_element(item['title'])
                    os.makedirs(dir, exist_ok=True)
                    os.chdir(dir)
                    section_created = True
                for video in item['videos']:
                    download_video(video_url = video[1], video_name = video[0])
            if section_created:
                os.chdir(base_dir)

        else:
            for section in item['content']:
                section_created = False
                if len(section['files']) is not 0:
                    if not section_created:
                        dir = sanitize_fs_element(item['title'])+'\\'+sanitize_fs_element(section['title'])
                        os.makedirs(dir, exist_ok=True)
                        os.chdir(dir)
                        section_created = True
                    for file in section['files']:
                        download_file(file)
                if len(section['videos']) is not 0:
                    if not section_created:
                        dir = sanitize_fs_element(item['title']) + '\\' + sanitize_fs_element(section['title'])
                        os.makedirs(dir, exist_ok=True)
                        os.chdir(dir)
                        section_created = True
                    for video in section['videos']:
                        download_video(video_url=video[1], video_name=video[0])
                if section_created:
                    os.chdir(base_dir)

    

def ocw_dl(course_url):
    course_name = course_url.split('/')[5]
    httpresponse = gethtml(course_url) 
    if httpresponse[0] != 200:
        if httpresponse[0] == 404:
            print('Invalid Course URL. No such course found!')
        else:
            print('An error occured while accessing', course_url, 'HTTP Status Code:', httpresponse[0])
    else:
        course_structure = generate_structure(httpresponse[1])
        print(*course_structure, sep="\n")
        extract_resources(course_structure)
        print(*course_structure, sep="\n")
        print('Total Videos: ', total_videos)
        print('Total Files: ', total_files)
        download_resources(course_structure, course_name)


ocw_dl('https://ocw.mit.edu/courses/economics/14-01sc-principles-of-microeconomics-fall-2011/')
    
        