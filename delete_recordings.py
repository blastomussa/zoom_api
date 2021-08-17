#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/13/2021
# Permanently deletes all recordings saved in Cloud_recordings log created by
# all_recodings.py from Zoom Cloud Storage
import csv
import urllib
import configparser
from jwt_token import *
from socket import gaierror # error handling

# set cloud recordings log file location
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    LOG = config['PATH']['CLOUD_RECORDINGS']
except configparser.Error:
    print("Configuration Error...config.ini not found")
    exit()
except KeyError:
    print("Configuration Error...config.ini not found")
    exit()


# Delete recordings
def delete_request(api_call):
    try:
        connection, header = init_connection()
        d = connection.request("DELETE", api_call, headers=header)
        response = connection.getresponse()
        data = response.read()
    # catch socket error in case of lost connection
    except gaierror as e:
        print("Failed to Connect")
        raise SystemExit(e)


def get_ids():
    # open csv
    ids = []
    with open(LOG, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row['id']
            ids.append(id)

    # return list of meetings to be deleted
    return ids


def delete_recordings():
    # uuids need to be doubly encoded; spec chars to hex twice
    # per zoom api docs
    ids = get_ids()
    for id in ids:
        i = urllib.parse.quote(id, safe='')
        id = urllib.parse.quote(i, safe='')
        api_call = "/v2/meetings/" + id + "/recordings?action=delete"
        delete_request(api_call)


if __name__ == '__main__':
    delete_recordings()
