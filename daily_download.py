#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/7/2021
# Downloads all Zoom cloud recordings from current day
import os
import time
import json
import requests
import configparser
from jwt_token import *
#import sys, errno # error handling
from socket import gaierror # error handling

# load config.ini to set global variables
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    recording_root = config['PATH']['RECORDING_ROOT']
    LOG = config['PATH']['LOG']
    RUN_LOG = config['PATH']['RUN_LOG']
except configparser.Error:
    print("Configuration Error...config.ini not found")
    exit()
except KeyError:
    print("Configuration Error...config.ini not found")
    exit()

# --------------->>>change all times for logs to ISO time format
# get start time for run log
t = time.localtime() # get struct_time
start_date = time.strftime("%Y-%m-%d", t)
start_time = time.strftime("%H:%M:%S", t)

# get api request and convert response to json
def get_request(api_call):
    try:
        connection, header = init_connection()
        connection.request("GET", api_call, headers=header)
        response = connection.getresponse()
        data = response.read()
        d = data.decode("utf-8")
        json_data = json.loads(d)
        return json_data
    # catch socket error in case of lost connection
    # -------------------->>>might need to add more exceptions
    except gaierror as e:
        log_run(start_date, "Failed to Connect",0,0)
        raise SystemExit(e)


# write log to csv file; path to log in config.ini
def log_results(date, date_time, id, host, topic, path):
    # check for log file, create if not found
    if(os.path.isfile(LOG) == False):
        file = open(LOG, "w")
        head = "download_date,record_date,status,meeting_id,host_name,topic,path_to_recording\n"
        file.writelines(head)
        file.close()

    # test existance of file and set status
    if(os.path.isfile(path) == True):
        status = "Success"
    else:
        status = "Failed"
        path = "N/A"

    # log results of download to LOG file
    file = open(LOG, "a")
    data = date + "," + date_time + "," + status + "," + id + "," + host + "," + topic + "," + path + "\n"
    file.writelines(data)
    file.close()

    return status


def log_run(start_date, start, success, fails):
    total_attemps = str(success + fails)

    # get end time of program
    t = time.localtime() # get struct_time
    end = time.strftime("%H:%M:%S", t)

    # check for log file, create if not found
    if(os.path.isfile(RUN_LOG) == False):
        file = open(RUN_LOG, "w")
        head = "date,start,end,total_attemps,success,fails\n"
        file.writelines(head)
        file.close()

    # log results of download to LOG file
    file = open(RUN_LOG, "a")
    data = start_date + "," + start + "," + end + "," + total_attemps + "," + str(success)  + "," + str(fails) + "\n"
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
    try:
        r = requests.get(url, stream = True)
        r.raise_for_status()
        with open(file_path, "wb") as video:
        	for chunk in r.iter_content(chunk_size = 1024):
        		if chunk:
        			video.write(chunk)
    # handle error; downloads will flag as failed in log_results with path check
    except IOError as e:
        pass
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.RequestException:
        pass
    except requests.exceptions.ConnectionError:
        pass


# get recording info, download/organize files, log results
def get_recordings(meetings):
    # accumulator
    number_of_downloads = 0
    number_of_fails = 0

    # loop over meetings list
    for meeting in meetings:
        id = meeting["uuid"]

        # get meeting info with download_url/token
        api_call = "/v2/meetings/" + id + "/recordings?include_fields=download_access_token"
        details = get_request(api_call)

        # get host details
        api_call = "/v2/users/" + details['host_id']
        host = get_request(api_call)

        # recording variables
        host_name = host["first_name"] + "_" + host["last_name"]
        topic = details["topic"]
        start = details["start_time"]
        access_token = details["download_access_token"]

        # get recording files list
        rec_files = details["recording_files"]

        # loop through files list to get download_url for mp4 file
        for file in rec_files:
            if(file["file_type"] == "MP4"):
                mp4_url = file["download_url"]

        # combine download_URL and download_access_token
        download_url = mp4_url + "?access_token=" + access_token

        # set path variables and check paths
        staff_root = os.path.join(recording_root, host_name)
        topic_path = os.path.join(staff_root, topic)
        check_paths(staff_root,topic_path)

        # create recording file name
        file_name = start[:10] + "_" + topic + ".mp4"
        mp4_path = os.path.join(topic_path, file_name)

        # if filename already exists change to more unique filename
        if(os.path.isfile(mp4_path) == True):
            file_name = start + "_" + topic + ".mp4"
            mp4_path = os.path.join(topic_path, file_name)

        # download recording and log file info
        download_video(download_url,mp4_path)

        # log results
        status = log_results(start_date, start, id, host_name, topic, mp4_path)

        # update accumulator
        if(status == "Success"): number_of_downloads = number_of_downloads + 1
        if(status == "Failed"): number_of_fails = number_of_fails + 1

    return number_of_downloads, number_of_fails


# called by main.py
def daily_download():
    # create api call to get recordings info from today dynamically
    t = time.localtime()
    date = time.strftime("%Y-%m-%d", t)
    recordings_call = "/v2/accounts/me/recordings?page_size=300&from=" + date

            #--------------->TEST CALL<----------------#
    #recordings_call = "/v2/accounts/me/recordings?from=2021-07-013&page_size=300"

    # get recordings json
    recordings = get_request(recordings_call)

    # if there are 0 recordings exit and log
    if(int(recordings["total_records"]) == 0):
        log_run(start_date, start_time, "N/A", 0, 0)
        return 0

    # get meeting list
    meetings = recordings["meetings"]

    # get recording info and download videos; log fails and success
    number_of_downloads, number_of_fails = get_recordings(meetings)

    # set next page token for pagination and to test for empty
    next_page_token = recordings["next_page_token"]

    # while next page token is not empty download meetings; handles multi pages
    while(next_page_token != ""):
        # create next page call
        api_call = recordings_call + "&next_page_token=" + next_page_token

        # get recordings json and meetings list
        recordings = get_request(api_call)
        meetings = recordings["meetings"]

        # if there isn't a next page, token is empty
        next_page_token = recordings["next_page_token"]

        # download recordings from next page
        d,f = get_recordings(meetings)
        number_of_downloads = number_of_downloads + d
        number_of_fails = number_of_fails + f

    # write to run_log
    log_run(start_date, start_time, number_of_downloads, number_of_fails)
    return 0


if __name__ == '__main__':
    daily_download()
