#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/7/2021
import time
import http.client
import json
import requests
import os
import configparser
from jwt_token import *

# load config.ini
config = configparser.ConfigParser()
config.read('config.ini')

recording_root = config['PATH']['RECORDING_ROOT']
LOG = config['PATH']['LOG']


#initiate https connection with api and form auth header
def init_connection():
    token = get_token()
    connection = http.client.HTTPSConnection("api.zoom.us")
    header = {
        'authorization': "Bearer " + token,
        'content-type': "application/json"
    }
    return connection, header


# get api request and convert response to json
def get_request(header, connection, api_call):
    connection.request("GET", api_call, headers=header)
    response = connection.getresponse()
    data = response.read()
    d = data.decode("utf-8")
    json_data = json.loads(d)
    return json_data


# write log to csv file; path to log in config.ini
def log_results(date, id, host, topic, path):
    if(os.path.isfile(LOG) == False):
        file = open(LOG, "w")
        head = "date_time,meeting_id,host_name,topic,path_to_recording\n"
        file.writelines(head)
        file.close()
    file = open(LOG, "a")
    data = date + "," + id + "," + host + "," + topic + "," + path +"\n"
    file.writelines(data)
    file.close()


# check paths of download locations and create if they don't exist
def check_paths(staff_root,topic_path):
    if(os.path.isdir(recording_root) == False):
        os.mkdir(recording_root)
    if(os.path.isdir(staff_root) == False):
        os.mkdir(staff_root)
    if(os.path.isdir(topic_path) == False):
        os.mkdir(topic_path)


# download mp4 file in 1024 byte chunks
def download_video(url,file_path):
    r = requests.get(url, stream = True)
    with open(file_path, "wb") as video:
    	for chunk in r.iter_content(chunk_size = 1024):
    		if chunk:
    			video.write(chunk)

            
# get recording info, download/organize files, log results
def get_recordings(header, connection, meetings):
    # loop over all meetings
    index = len(meetings)
    while(index > 0):
        index = index - 1
        meeting = meetings[index]
        id = meeting["uuid"]

        # get meeting info with download_url/token
        api_call = "/v2/meetings/" + id + "/recordings?include_fields=download_access_token"
        details = get_request(header,connection,api_call)

        # get host details
        api_call = "/v2/users/" + details['host_id']
        host = get_request(header,connection,api_call)

        # recording variables
        host_name = host["first_name"] + "_" + host["last_name"]
        topic = details["topic"]
        start_time = details["start_time"]
        access_token = details["download_access_token"]

        # get download url for mp4
        rec_files = details["recording_files"]
        length_files = len(rec_files)
        while(length_files > 0):
            length_files = length_files - 1
            file = rec_files[length_files]

            # filter for mp4 file
            if(file["file_type"] == "MP4"):
                mp4_url = file["download_url"]

        # combine download_URL and download_access_token
        download_url = mp4_url + "?access_token=" + access_token

        # paths
        staff_root = os.path.join(recording_root, host_name)
        topic_path = os.path.join(staff_root, topic)
        check_paths(staff_root,topic_path)

        # create recording file name
        file_name = start_time[:10] + "_" + topic + ".mp4"

        # file name collision prevention
        mp4_path = os.path.join(topic_path, file_name)
        if(os.path.isfile(mp4_path) == True):
            file_name = start_time + "_" + topic + ".mp4"
            mp4_path = os.path.join(topic_path, file_name)

        # download recording and log file info
        # add protections against double downloads
        # maybe hash time and ID from LOG to compare; might take too long...
        download_video(download_url,mp4_path)
        log_results(start_time, id, host_name, topic, mp4_path)


def main():
    # establish https connection and authorization header
    connection, header = init_connection()

    # get recordings info from today(dynamic)
    t = time.localtime()
    date = time.strftime("%Y-%m-%d", t)
    rec_call = "/v2/accounts/me/recordings?page_size=300&from=" + date

            #--------------->TEST CALL<----------------#
    #rec_call = "/v2/accounts/me/recordings?from=2021-08-05&page_size=1"

    # get recordings json and meetings list
    recordings = get_request(header, connection, rec_call)
    meetings = recordings["meetings"]

    # get recording info and download videos
    get_recordings(header, connection, meetings)

    # next page handling
    next_page_token = recordings["next_page_token"]
    while(next_page_token != ""):
        api_call = rec_call + "&next_page_token=" + next_page_token
        recordings = get_request(header, connection, api_call)
        meetings = recordings["meetings"]
        next_page_token = recordings["next_page_token"]
        get_recordings(header, connection, meetings)


if __name__ == '__main__':
    main()
