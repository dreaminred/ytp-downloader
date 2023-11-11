from pytube import Channel, YouTube

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pandas as pd
import os

def getAllVideoURLs(channel_name: str):

    full_url = 'https://www.youtube.com/' + channel_name + '/videos'

    driver = webdriver.Chrome()

    driver.get(full_url)
    time.sleep(3)

    item = []
    SCROLL_PAUSE_TIME = 1
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    item_count = 180

    while item_count > len(item):
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height


    data = []
    try:
        for e in WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#details'))):
            title = e.find_element(By.CSS_SELECTOR,'a#video-title-link').get_attribute('title')
            vurl = e.find_element(By.CSS_SELECTOR,'a#video-title-link').get_attribute('href')
            views= e.find_element(By.XPATH,'.//*[@id="metadata"]//span[@class="inline-metadata-item style-scope ytd-video-meta-block"][1]').text
            date_time = e.find_element(By.XPATH,'.//*[@id="metadata"]//span[@class="inline-metadata-item style-scope ytd-video-meta-block"][2]').text
            data.append({
                'video_url':vurl,
                'title':title,
                'date_time':date_time,
                'views':views
            })
    except:
        pass

    item = data
    print("Number of videos found: " + str(len(item)))
    videos_df = pd.DataFrame(item)
    return videos_df

def downloadVideosAll(video_list, output_dir):

    for video in video_list.iterrows():
        video_title = video[1]['title'].replace('"','_').replace(" ","_").replace("/","_")
        video_url = video[1]['video_url']
        yt = YouTube(url=video_url)
        fileName = video_title + '.mp4'

        print(fileName)

        if (os.path.exists('videos/' + fileName)):
            print("Video already exists.")
            continue
        try:
            yt.streams.get_highest_resolution().download(output_path=output_dir, filename=fileName)
        except:
            print("Age restriction.")

def main(channel_name, fileDir):
    channel_videos = getAllVideoURLs(channel_name)
    print('Retrieved video list.')
    downloadVideosAll(channel_videos, fileDir)
    print('Downloaded all videos.')


if __name__ == '__main__':
    channel_name = sys.argv[1]
    output_dir = sys.argv[2]
    main(channel_name, output_dir)
