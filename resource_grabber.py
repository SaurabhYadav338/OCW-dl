import urllib3
import certifi
import time
import os
import sys
from tqdm import tqdm

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
def download_file(url):
    http_connection = http.request('GET', url, preload_content = False)
    filename = url.split('/')[-1]
    if (http_connection.status != 200):
        print('Failed to download', filename)
    else:
        file_size = int(http_connection.headers.get("Content-Length"))
        if os.path.exists(os.getcwd()+'\\'+filename):
            if os.path.getsize(os.getcwd()+'\\'+filename) == file_size:
                print('[download]', filename, 'has already been downloaded\n')
        else:
            with open(filename, 'wb') as filehandle:
                print('Downloading:', filename)
                start_time = time.time()
                pbar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, leave=False, desc='[download]', dynamic_ncols=True, file=sys.stdout)
                for download_stream in http_connection.stream():
                    downloaded = len(download_stream)
                    pbar.update(downloaded)
                    filehandle.write(download_stream)
            filehandle.close()
            pbar.close()
            http_connection.release_conn()
            elapsed = time.time() - start_time
            elapsed = round(elapsed)
            elapsed_minutes = int(elapsed / 60)
            elapsed_seconds = elapsed % 60
            if (elapsed_minutes != 0):
                elapsed_time = str(elapsed_minutes) + ' minutes ' + str(elapsed_seconds) + ' seconds'
            else:
                elapsed_time = str(elapsed_seconds) + ' seconds'
            success_message = f"\rDownloaded {(file_size/1048576):.2f}MiBs in {elapsed_time}\n"
            success_message += ' ' * (70 - len(success_message))
            print(success_message)
"""download_file('https://ocw.mit.edu/courses/economics/14-01sc-principles-of-microeconomics-fall-2011/unit-2-consumer-theory/preferences-and-utility/MIT14_01SCF11_rec02.pdf')"""
