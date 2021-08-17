#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/13/2021
# gets all recordings from an account and logs them to csv file
# download 75 months worth of cloud recording details
# meant to run as a standalone script to generate full list of recordings
# over a specific time frame: MONTHS variables
import os
import json
import time
import configparser
from jwt_token import *
from datetime import date, timedelta

# how many months back to you want to download ids for
MONTHS = 75

# set log file location
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
    except gaierror as e:
        raise SystemExit(e)


def get_info(meetings):
    # create log
    file = open(LOG, "w")
    head = "id,start_time\n"
    file.writelines(head)

    # loop over meetings list
    for meeting in meetings:
        id = meeting["uuid"]
        start_time = meeting["start_time"]

        # get recording info
        api_call = "/v2/meetings/" + id + "/recordings"
        details = get_request(api_call)

        data = id + "," + start_time + "\n"
        file.writelines(data)

    file.close()


def main():
    current_date = date.today()
    from_date = current_date
    i = 0
    while(i < MONTHS):
        # update accumulator
        i = i + 1

        # update to and from dates
        to_date = from_date
        from_date = to_date - timedelta(days=29)

        # build api call
        call = "/v2/accounts/me/recordings?from="+ from_date.isoformat() + "&to=" + to_date.isoformat() + "&page_size=300"

        # get recordings json and meetings list
        recordings = get_request(call)
        meetings = recordings["meetings"]

        # log recording info to csv
        get_info(meetings)


if __name__ == '__main__':
    main()
