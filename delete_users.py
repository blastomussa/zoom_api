#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/16/2021
# Deletes users from a specified csv that includes user id
# VERY DESTRUCTIVE...do not run if you do not understand the consequenses
import os
import json
import time
import configparser
import csv
from jwt_token import *

# set log file location
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    USER_LOG = config['PATH']['USERS']
except configparser.Error:
    print("Configuration Error...config.ini not found")
    exit()
except KeyError:
    print("Configuration Error...config.ini not found")
    exit()


# Delete users
def delete_request(api_call):
    try:
        connection, header = init_connection()
        d = connection.request("DELETE", api_call, headers=header)
        response = connection.getresponse()
        data = response.read()
        print(data)
    # catch socket error in case of lost connection
    except gaierror as e:
        print("Failed to Connect")
        raise SystemExit(e)


# get ids from csv
def get_ids():
    # open csv
    ids = []
    with open(USER_LOG, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row['id']
            ids.append(id)

    # return list of meetings to be deleted
    return ids


# delete users
def delete_users():
    ids = get_ids()

    for id in ids:
        api_call = "/v2/users/" + id + "?action=delete"
        delete_request(api_call)


if __name__ == '__main__':
    delete_users()
