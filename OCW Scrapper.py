# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:43:45 2019

@author: Saurabh
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 17:56:24 2019

@author: Saurabh
"""

from bs4 import BeautifulSoup
import urllib3
import certifi
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

count = 0
matches = {}
parsed = []
num_sections = 0
filehandle = open('C:/Users/Saurabh/Desktop/sections.txt','a')

def gethtml(resource_url):
    global count
    count += 1
    print("Parsing: ", resource_url, "Request Count:", count)
    success = False
    httpresponse = http.request("GET", resource_url)
    while(not success):
        try:
            httpresponse = http.request("GET", resource_url)
            success = True
        except:
            print("Network Failure. Retrying...")
    if httpresponse.status == 404:
        print('Invalid Course URL. No such course found!')
    elif httpresponse.status != 200:
        print('An error occured while accessing', resource_url, 'HTTP Status Code:', httpresponse.status)
    return [httpresponse.status, httpresponse.data]


def parsenode(resource_url):
    global filehandle, num_sections
    httpresponse = gethtml(resource_url)
    if httpresponse[0] == 200:
        parsetree = BeautifulSoup(httpresponse[1], 'lxml')
        if parsetree.find_all(id = "course_nav"):
            nav = parsetree.find_all(id = "course_nav")
            for link in nav[0].find_all('a'):
                if link.string is not None:
                    section_name = (link.string).strip();
                    if section_name in matches.keys():
                        matches.update({section_name : matches[section_name]+1})
                        print("Found another instance of:", section_name)
                    else:
                        num_sections += 1
                        print("Found new section:", section_name, "Total Sections:", num_sections)
                        matches.update({section_name : 1})
                    
        else:
            n = 1
            for course in parsetree.find_all(class_="course_title"):
                for link in course.find_all('a'):
                    print("#", n)
                    n += 1
                    parsenode('https://ocw.mit.edu'+link['href'])
    else:
        print('HTTP ERROR')
    return
page = gethtml('https://ocw.mit.edu/courses/find-by-department/')
depts = BeautifulSoup(page[1], 'lxml').find_all(class_="deptList")
for dept in depts:
    for link in dept.find_all('a'):
        if link not in parsed:
            link = 'https://ocw.mit.edu'+link['href']
            parsed.append(link)
            parsenode(link)
current = 0
done = 0
for key in matches:
    if matches[key] > current:
        current = matches[key]
while done < len(matches):
    for key in matches:
        if matches[key] == current:
            done += 1
            filehandle.write(key+' : '+str(matches[key])+'\n')
    current -= 1
filehandle.close()