#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/7/2021
import jwt
import time
import http.client
import configparser

def get_token():
    # get api ket and secret from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['ZOOM_CLIENT']['API_KEY']
    secret = config['ZOOM_CLIENT']['SECRET']

    # generate timestamps in epoch time for payload; ttl = 5 hrs
    t = time.time()
    time_stamp = int(t)
    ttl = int(18000) + time_stamp

    # create payload
    payload_data = {
        "aud": None,
        "iss": api_key,
        "exp": ttl,
        "iat": time_stamp
    }

    # encode JWT token; encode() method defaults to HS256 encoding
    token = jwt.encode(
        payload=payload_data,
        key=secret
    )
    return token


# create auth header and init https connection with Zoom API
def init_connection():
    token = get_token()
    connection = http.client.HTTPSConnection("api.zoom.us")
    header = {
        'authorization': "Bearer " + token,
        'content-type': "application/json"
    }
    return connection, header
