# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:49:16 2019

@author: Saurabh
"""

from bs4 import BeautifulSoup
import urllib3
import certifi
import logging
import time
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def gethtml(resource_url):
    start = time.time()
    print("Requesting:", resource_url)
    time.clock() 
    httpresponse = http.request("GET", resource_url)
    print("Time Taken:", time.time() - start, "seconds")
    print("Successful")
    return [httpresponse.status, httpresponse.data]

def get_sections(course_page):
    parsetree = BeautifulSoup(course_page, 'lxml')
    navs = parsetree.find_all(id="course_nav")
    sections = []
    for nav in navs:
        for section in nav.find_all('a'):
            linktext = section.string
            if linktext != None:
                sections.append([(section.string).strip(), 'https://ocw.mit.edu'+section['href']+'/'])
    return sections
    
def get_videos(videos_pageurl):
    httpresponse = gethtml(videos_pageurl)
    video_list = []
    if(httpresponse[0] != 200):
        exit("Unable to fetch Video listing")
    parsetree = BeautifulSoup(httpresponse[1], 'lxml')
    mediacontainer = parsetree.find(id="course_inner_media_gallery")
    for media in mediacontainer.find_all(class_="medialisting"):
        videolink = media.find('a');
        video_list.append([videolink['title'], "https://ocw.mit.edu"+videolink['href']+'/'])
    return video_list
    

def ocw_dl(course_url):
    httpresponse = gethtml(course_url) 
    if httpresponse[0] != 200:
        if httpresponse[0] == 404:
            print('Invalid Course URL. No such course found!')
        else:
            print('An error occured while accessing', course_url, 'HTTP Status Code:', httpresponse[0])
    else:
        course_sections = get_sections(httpresponse[1])
        available_sections = {}
        for section in course_sections:
            if 'lecture video' in section[0].lower():
                available_sections['videos'] = section
            elif 'slides' in section[0].lower():
                available_sections['slides'] = section
        video_list = get_videos(available_sections['videos'][1])
        for video in video_list:
            print(video[0],"\t",video[1],"\n")



ocw_dl('https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-034-artificial-intelligence-fall-2010/')
    
        