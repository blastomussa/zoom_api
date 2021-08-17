#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/16/2021
# Gets a CSV of all users in Zoom account exports id and email
import os
import json
import time
import configparser
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


def get_users(users):
    # create log
    if(os.path.isfile(USER_LOG) == False):
        file = open(USER_LOG, "a")
        head = "username,id\n"
        file.writelines(head)
        file.close()

    file = open(USER_LOG, "a")

    for user in users:
        uname = user["email"]
        id = user["id"]
        data = uname + "," + id + "\n"
        file.writelines(data)

    file.close()

    
def main():
    # create api call
    users_call = "/v2/users?page_size=300"

    # get users json
    user_page = get_request(users_call)
    users = user_page["users"]


    # log users into csv
    get_users(users)

    # next page handling
    next_page_token = user_page["next_page_token"]

    # while next page token is not empty download meetings; handles multi pages
    while(next_page_token != ""):
        # create next page call
        api_call = users_call + "&next_page_token=" + next_page_token

        # get users json
        user_page = get_request(api_call)
        users = user_page["users"]

        # log users into csv
        get_users(users)

        # next page handling
        next_page_token = user_page["next_page_token"]


if __name__ == '__main__':
    main()
