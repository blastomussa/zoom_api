#!/usr/bin/env python3
#Author: Blastomussa
#Date 8/7/2021
import jwt
import time
import configparser

def get_token():

    # get api ket and secret from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['ZOOM_CLIENT']['API_KEY']
    secret = config['ZOOM_CLIENT']['SECRET']

    # generate timestamps in epoch time for payload; ttl = 300 minutes
    # may need to adjust ttl for long download times
    t = time.time()
    time_stamp = int(t)
    ttl = int(18000) + time_stamp

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
