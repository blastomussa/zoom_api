#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/20/2021
# Class based implementation of javascript web token application for Zoom API
# best used in server-to-server applications and automations
import jwt
import time
import requests
from simplejson.scanner import JSONDecodeError
from requests.exceptions import ConnectionError


class zoompy:
    def __init__(self,api_key,api_secret):
        self.key = api_key
        self.secret = api_secret
        self.root_url = "https://api.zoom.us/v2"

###--------------------JAVASCRIPT WEB TOKEN AUTHORIZATION----------------###
    def _authorize(self):
        # generate timestamps in epoch time for payload; ttl = 5 minutes
        time_stamp = int(time.time())
        ttl = int(300) + time_stamp
        # create authorization header
        payload = {
            "aud": None,
            "iss": self.key,
            "exp": ttl,
            "iat": time_stamp
        }
        # encode JWT token; encode() method defaults to HS256 encoding
        token = jwt.encode(payload=payload,key=self.secret)
        # build authorization haeder for use in requests
        header = {
            'authorization': "Bearer " + token,
            'content-type': "application/json"
        }
        return header


###---------------------------REST API METHODS----------------------------###
    # PASSED TEST
    def _get(self,api_call):
        try:
            header = self._authorize()
            call = self.root_url + api_call
            response = requests.get(call,headers=header)
            # do something with status codes...
            #print("Status Code", response.status_code)
            return response.json()
        # catch socket error in case of lost connection and bad endpoint error
        except (ConnectionError, JSONDecodeError)  as e:
            exit(1)


    def _post(self,api_call,data):
        try:
            header = self._authorize()
            call = self.root_url + api_call
            response = requests.post(call,headers=header,json=data)
            # do something with status codes...
            print("Status Code", response.status_code)
            return response.json()
        except (ConnectionError, JSONDecodeError)  as e:
            exit(1)


    def _put(self,api_call,data):
        try:
            header = self._authorize()
            call = self.root_url + api_call
            response = requests.put(call,headers=header,json=data)
            # do something with status codes...
            print("Status Code", response.status_code)
            return response.json()
        # catch socket error in case of lost connection and bad endpoint error
        except (ConnectionError, JSONDecodeError)  as e:
            exit(1)


    def _patch(self,api_call,data):
        try:
            header = self._authorize()
            call = self.root_url + api_call
            response = requests.patch(call,headers=header,json=data)
            return response.status_code
        except (ConnectionError, JSONDecodeError)  as e:
            exit(1)


    def _delete(self,api_call):
        try:
            header = self._authorize()
            call = self.root_url + api_call
            response = requests.delete(call,headers=header)
            # do something with status codes...
            print("Status Code", response.status_code)
            return response.json()
        except (ConnectionError, JSONDecodeError)  as e:
            exit(1)


###---------------------------ZOOM API CALLS----------------------------###
    # get all licensed users for account (basic and premium)
    def get_users(self):
        endpoint = "/users"
        params = "?page_size=300"
        call = endpoint + params
        data = self._get(call)
        users = data['users']
        # next page handling
        next = data['next_page_token']
        while(next != ""):
            next_page = call + "&next_page_token=" + next
            data = self._get(next_page)
            u = data['users']
            users = users + u
            next = data["next_page_token"]
        return users


    # get user json
    # can also pass email as ID
    def get_user(self,id):
        endpoint = "/users/"
        call = endpoint + id
        user = self._get(call)
        return user


    def get_userID(self,email):
        users = self.get_users()
        dict = {}
        for user in users:
            dict[user['email']] = user['id']
        try:
            id = dict[email]
            return id
        except KeyError:
            message = "No user found for:" + str(email)
            return message


    def update_user(self,id,json):
        endpoint = "/users/"
        call = endpoint + id

        response = self._patch(call,json)
        return response
